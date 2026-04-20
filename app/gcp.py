"""Centralized Google Cloud (Vertex AI) client initialization."""
import os
import vertexai
from vertexai.generative_models import GenerativeModel
from dotenv import load_dotenv

load_dotenv(override=True)

# State variables to hold the initialization result, accessible across the app
GEMINI_MODEL = None
IS_CONFIGURED = False
CONFIG_ERROR = None

def initialize_vertexai():
    """
    Initializes the Vertex AI client based on environment variables.
    This function is designed to be called once at application startup.
    It sets the global state variables (GEMINI_MODEL, IS_CONFIGURED, CONFIG_ERROR).
    """
    global GEMINI_MODEL, IS_CONFIGURED, CONFIG_ERROR

    # Prevent re-initialization if already attempted
    if IS_CONFIGURED or CONFIG_ERROR:
        return

    # Check for a setup error from the initial credential handling in app.py
    # This provides a more specific error message than just "variable not set".
    setup_error = os.getenv("GCP_SETUP_ERROR")
    if setup_error:
        CONFIG_ERROR = setup_error
        return

    gcp_project = os.getenv("GCP_PROJECT")
    gcp_location = os.getenv("GCP_LOCATION")
    gcp_creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    gcp_model_name = os.getenv("GCP_MODEL_NAME", "gemini-2.5-pro")

    missing_vars = []
    if not gcp_project: missing_vars.append("GCP_PROJECT")
    if not gcp_location: missing_vars.append("GCP_LOCATION")
    if not gcp_creds_path:
        missing_vars.append("GOOGLE_APPLICATION_CREDENTIALS (derived from GCP_CREDENTIALS_JSON in secrets)")

    if missing_vars:
        CONFIG_ERROR = f"The following required Google Cloud environment variables are not set: {', '.join(missing_vars)}"
        return

    if not os.path.exists(gcp_creds_path):
        CONFIG_ERROR = f"The specified GOOGLE_APPLICATION_CREDENTIALS file does not exist at: {gcp_creds_path}"
        return

    try:
        vertexai.init(project=gcp_project, location=gcp_location)
        GEMINI_MODEL = GenerativeModel(gcp_model_name)
        IS_CONFIGURED = True
    except Exception as e:
        CONFIG_ERROR = f"Failed to initialize Vertex AI SDK. Error: {e}"

# Automatically initialize when the module is first imported.
initialize_vertexai()