"""Main Temporiq AI application."""
import streamlit as st

# Page configuration must be the first Streamlit command.
st.set_page_config(
    page_title="Temporiq AI",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from dotenv import load_dotenv
import os
import json
import tempfile
import logging
import streamlit.components.v1 as components

def setup_gcp_credentials_from_env():
    """
    Handles GCP credentials for production environments.
    If the `GCP_CREDENTIALS_JSON` environment variable is found (e.g., from a host's secret manager),
    this function writes its content to a temporary file and sets the `GOOGLE_APPLICATION_CREDENTIALS`
    environment variable to point to that file's path. This avoids committing secret files.
    This function is designed to be called BEFORE `app.gcp` is initialized.
    """
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        return

    gcp_creds_json_str = None

    # 1. Safely read from Streamlit Secrets first (completely bypasses os.environ caching bugs)
    try:
        if "GCP_CREDENTIALS_JSON" in st.secrets:
            gcp_creds_json_str = st.secrets["GCP_CREDENTIALS_JSON"]
    except Exception:
        pass

    # 2. Fallback to standard environment variable
    if not gcp_creds_json_str:
        gcp_creds_json_str = os.getenv("GCP_CREDENTIALS_JSON")

    if gcp_creds_json_str:
        try:
            # --- ROBUSTNESS CHECK ---
            # If the user accidentally pasted the whole TOML line from the helper script
            # as the value, the string will start with "GCP_CREDENTIALS_JSON = ".
            # We can strip this prefix to recover the actual JSON content.
            if isinstance(gcp_creds_json_str, str) and gcp_creds_json_str.strip().startswith("GCP_CREDENTIALS_JSON"):
                logging.warning("Detected full TOML line in secret value. Attempting to parse content.")
                gcp_creds_json_str = gcp_creds_json_str.split('=', 1)[-1].strip()
                # If the value was single-quoted or double-quoted, strip the quotes.
                if (gcp_creds_json_str.startswith("'") and gcp_creds_json_str.endswith("'")) or \
                   (gcp_creds_json_str.startswith('"') and gcp_creds_json_str.endswith('"')):
                    gcp_creds_json_str = gcp_creds_json_str[1:-1]

            # Handle case where Streamlit Secrets parsed it directly into a dictionary natively
            if isinstance(gcp_creds_json_str, dict):
                creds_dict = gcp_creds_json_str
            else:
                creds_dict = json.loads(gcp_creds_json_str, strict=False)

                # Robustness check: if it was doubly stringified, unpack it again
                if isinstance(creds_dict, str):
                    creds_dict = json.loads(creds_dict, strict=False)

            if not isinstance(creds_dict, dict):
                raise TypeError(f"Expected a dictionary, got {type(creds_dict)}.")

            # Create a temporary file and use json.dump to write the credentials correctly.
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as temp_creds_file:
                json.dump(creds_dict, temp_creds_file)
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp_creds_file.name
        except (json.JSONDecodeError, TypeError) as e:
            # If parsing fails, we set a specific error message that can be picked up by the gcp module.
            # This makes debugging in production much easier.
            error_message = f"Failed to parse GCP_CREDENTIALS_JSON from secrets. Please ensure it's a valid, single-line JSON string. Error: {e}"
            
            # Extract and display the exact string snippet around the error using repr() to reveal hidden characters
            if isinstance(e, json.JSONDecodeError) and hasattr(e, 'doc') and hasattr(e, 'pos'):
                error_snippet = repr(e.doc[max(0, e.pos - 40) : min(len(e.doc), e.pos + 40)])
                error_message += f" | Debug Snippet (around char {e.pos}): {error_snippet}"
                
            logging.error(error_message)
            os.environ["GCP_SETUP_ERROR"] = error_message

# Set up production credentials first, then load .env for local development.
setup_gcp_credentials_from_env()
load_dotenv()

# Configure logging to reduce httpx verbosity, which is used by supabase-py.
# This will hide the "INFO" messages about successful HTTP requests.
logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

# Initialize Google Cloud services from the centralized handler
from app.gcp import initialize_vertexai
initialize_vertexai()

from app.styles import inject_custom_css
from views.setup import render_workflows_page # type: ignore
from views.dashboard import render_tracker_page # type: ignore
from views.auth import render_auth_page # type: ignore
from views.reporting import render_reporting_page # type: ignore
from views.import_data import render_import_page # type: ignore
from views.user_guide import render_user_guide_page # type: ignore
from views.status import render_status_page # type: ignore
from app.database import AuthDB
# Inject custom CSS
inject_custom_css()

# Inject CSS to make all sidebar buttons uniform width and left-aligned.
st.markdown("""
    <style>
        /*
        The Streamlit sidebar uses a flexbox layout. By default, flex items (like button containers)
        don't stretch to fill the available width. This CSS forces the button's container to be full-width.
        */
        section[data-testid="stSidebar"] div[data-testid="stButton"] {
            width: 100%;
        }
        /*
        This ensures the button element itself fills its container and aligns the
        text and icon to the left for a clean, uniform look.
        */
        section[data-testid="stSidebar"] div[data-testid="stButton"] > button {
            width: 100%;
            justify-content: flex-start;
        }
    </style>
""", unsafe_allow_html=True)

# Check for user in session state, trying to retrieve from Supabase if not present
if 'user' not in st.session_state:
    with st.spinner("Authenticating..."):
        st.session_state.user = AuthDB.get_current_user()

# If user is not authenticated, render the auth page
if not st.session_state.user:
    # --- Logged-out state ---
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Login"

    st.sidebar.title("⏱️ Temporiq AI")
    
    if st.sidebar.button("🔐 Login", key="nav_login", use_container_width=True):
        st.session_state.current_page = "Login"
        st.rerun()

    page = st.session_state.get("current_page", "Login")
    if page == "Login":
        render_auth_page()
else:
    # --- Logged-in state ---
    # Initialize session state for a logged-in user
    if "current_workflow_id" not in st.session_state:
        st.session_state.current_workflow_id = None
    if "current_workflow" not in st.session_state:
        st.session_state.current_workflow = None

    # If the user just logged in (page is 'Login' or 'Status') or the page is not set, default to Workflows.
    # If the user just logged in (current page is 'Login') or the page is not set, default to Workflows.
    if "current_page" not in st.session_state or st.session_state.current_page == "Login":
        st.session_state.current_page = "Workflows"
    
    # Set user_id from the authenticated user object
    st.session_state.user_id = st.session_state.user['id']

    # Main navigation
    st.sidebar.title("⏱️ Temporiq AI")
    st.sidebar.write("Select a page below to manage workflows or track active cases.")

    if st.sidebar.button("⚙️ Workflows", key="nav_setup", use_container_width=True):
        st.session_state.current_page = "Workflows"
        st.rerun()

    if st.sidebar.button("⏱️ Tracker", key="nav_dashboard", use_container_width=True):
        st.session_state.current_page = "Tracker"
        st.rerun()

    if st.sidebar.button("📈 Reporting", key="nav_reporting", use_container_width=True):
        st.session_state.current_page = "Reporting"
        st.rerun()
        
    if st.sidebar.button("📥 Import Data", key="nav_import", use_container_width=True):
        st.session_state.current_page = "Import Data"
        st.rerun()
        
    if st.sidebar.button("📖 User Guide", key="nav_user_guide", use_container_width=True):
        st.session_state.current_page = "User Guide"
        st.rerun()

    if st.sidebar.button("⚙️ Account & System Status", key="nav_status", use_container_width=True):
        st.session_state.current_page = "Status"
        st.rerun()

    st.sidebar.markdown("---")
    if st.sidebar.button("Logout", use_container_width=True):
        AuthDB.sign_out()
        # Clear all session state keys on logout
        for key in st.session_state.keys():
            del st.session_state[key]
        st.rerun()

    # Render the appropriate page
    page = st.session_state.get("current_page", "Workflows")
    if page == "Workflows":
        render_workflows_page(st.session_state.user_id)
    elif page == "Tracker":
        render_tracker_page(st.session_state.user_id)
    elif page == "Reporting":
        render_reporting_page(st.session_state.user_id)
    elif page == "Import Data":
        render_import_page(st.session_state.user_id)
    elif page == "User Guide":
        render_user_guide_page(st.session_state.user_id)
    elif page == "Status":
        render_status_page(st.session_state.user)
        
        st.markdown("---")
        st.subheader("🔐 Account Settings")
        with st.expander("Update Password"):
            with st.form("update_password_form"):
                new_pass = st.text_input("New Password", type="password")
                confirm_pass = st.text_input("Confirm Password", type="password")
                if st.form_submit_button("Update Password"):
                    if new_pass and new_pass == confirm_pass:
                        try:
                            AuthDB.update_user_password(new_pass)
                            st.success("Password updated successfully!")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.error("Passwords do not match.")
