"""System Status Check page."""
import streamlit as st
import os
from app.database import supabase
from app.gcp import IS_CONFIGURED, CONFIG_ERROR

def render_detailed_status_page():
    """Renders the detailed view for admins."""
    st.markdown("Use this page to verify your application's configuration and external service connections.")
    st.markdown("---")
    
    # Check if running in Streamlit Cloud to provide context-aware hints
    is_streamlit_cloud = "STREAMLIT_SHARING_MODE" in os.environ and os.environ["STREAMLIT_SHARING_MODE"] == "true"
    config_location = "Streamlit Secrets" if is_streamlit_cloud else "`.env` file"

    st.subheader("Configuration and Connection Status")
    
    st.markdown("#### Environment Variables")
    
    # Supabase
    st.write("**Supabase:**")
    if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"): st.success(f"✓ `SUPABASE_URL` and `SUPABASE_KEY` are set.")
    else: st.error(f"✗ `SUPABASE_URL` or `SUPABASE_KEY` is NOT set. Please add them to your {config_location}.")

    # Google Cloud
    gcp_project, gcp_location, gcp_creds_path = os.getenv("GCP_PROJECT"), os.getenv("GCP_LOCATION"), os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    st.write("**Google Cloud (Vertex AI):**")
    if gcp_project: st.success(f"✓ `GCP_PROJECT` is set: `{gcp_project}`")
    else: st.error(f"✗ `GCP_PROJECT` is NOT set. Please add it to your {config_location}.")
    
    if gcp_project and "your-gcp-project-id" in gcp_project:
        st.warning("  - **Hint:** It looks like you're using the example project ID. You need to replace this placeholder with your actual GCP Project ID.")

    if gcp_location: st.success(f"✓ `GCP_LOCATION` is set: `{gcp_location}`")
    else: st.error(f"✗ `GCP_LOCATION` is NOT set. Please add it to your {config_location}.")

    # Check for credentials based on environment
    if is_streamlit_cloud:
        if os.getenv("GCP_CREDENTIALS_JSON"):
            st.success("✓ `GCP_CREDENTIALS_JSON` is set in Streamlit Secrets.")
        else:
            st.error("✗ `GCP_CREDENTIALS_JSON` is NOT set in Streamlit Secrets.")
    else: # Local environment
        if gcp_creds_path:
            st.success(f"✓ `GOOGLE_APPLICATION_CREDENTIALS` is set.")
            if os.path.exists(gcp_creds_path): st.success(f"  - File found at path.")
            else:
                st.error(f"  - ✗ File NOT found at path: `{gcp_creds_path}`")
        else:
            st.error("✗ `GOOGLE_APPLICATION_CREDENTIALS` is NOT set. You must set this in your terminal before running the app.")

    st.markdown("---")
    st.markdown("#### Connection Tests")

    # Test Supabase Connection
    st.write("**Supabase Connection:**")
    if supabase:
        try:
            supabase.table('workflows').select('id').limit(1).execute()
            st.success("✓ Successfully connected to Supabase.")
        except Exception as e:
            st.error("✗ Failed to connect to Supabase. This usually means your Supabase URL or Key is incorrect.")
            with st.expander("Click to see the full error message"):
                st.code(str(e))
    else:
        st.error("✗ Supabase client failed to initialize. This usually means your `SUPABASE_URL` is invalid or missing from your `.env` file.")

    # Test Vertex AI Connection
    st.write("**Vertex AI Connection:**")
    if IS_CONFIGURED:
        st.success("✓ Successfully connected to Vertex AI.")
    else:
        st.error("✗ Failed to connect to Vertex AI.")
        if CONFIG_ERROR:
            with st.expander("Click to see the full error message"):
                st.code(CONFIG_ERROR)

def render_simple_status_page():
    """Renders a simplified status view for non-admin users."""
    st.markdown("This page shows the operational status of our key services.")
    st.markdown("---")

    supabase_ok = False
    vertex_ai_ok = IS_CONFIGURED

    # Test Supabase
    try:
        if supabase:
            supabase.table('workflows').select('id').limit(1).execute()
            supabase_ok = True
    except Exception:
        supabase_ok = False

    # Display status
    st.subheader("Service Status")
    
    if supabase_ok:
        st.success("✓ **Database Connection:** Operational")
    else:
        st.error("✗ **Database Connection:** Experiencing Issues")

    if vertex_ai_ok:
        st.success("✓ **AI Service Connection:** Operational")
    else:
        st.error("✗ **AI Service Connection:** Experiencing Issues")

    st.markdown("---")

    if supabase_ok and vertex_ai_ok:
        st.success("✅ **All systems are operational.**")
    else:
        st.warning("⚠️ One or more systems are experiencing issues. Some features may be unavailable. Our team has been notified.")

def render_status_page(user: dict):
    """Renders the System Status Check page based on user role."""
    st.title("⚙️ System Status")
    
    # Read the admin email from environment variables. Fallback to None if not set.
    admin_email = os.getenv("ADMIN_EMAIL")
    user_email = user.get("email")

    # If ADMIN_EMAIL is set and matches the user's email, show the detailed view.
    if admin_email and user_email == admin_email:
        render_detailed_status_page()
    else:
        render_simple_status_page()