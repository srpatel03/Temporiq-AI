"""Authentication page for user login and sign-up."""
import streamlit as st
from app.database import AuthDB
import time

def render_auth_page():
    """Renders the authentication page with login, sign-up, or password reset."""
    st.title("⏱️ Temporiq AI")

    if 'auth_error' in st.session_state:
        st.error(f"Link Error: {st.session_state.auth_error}")
        del st.session_state.auth_error

    if 'show_forgot_password' not in st.session_state:
        st.session_state.show_forgot_password = False

    if st.session_state.show_forgot_password:
        st.subheader("Reset Your Password")
        with st.form("forgot_password_form"):
            email = st.text_input("Enter your email address")
            submitted = st.form_submit_button("Send Reset Link")
            if submitted:
                try:
                    AuthDB.admin_reset_password(email)
                    st.success("If an account exists for this email, an email with a temporary password has been sent.")
                except Exception as e:
                    st.error(str(e))
        if st.button("← Back to Login"):
            st.session_state.show_forgot_password = False
            st.rerun()
    else:
        st.markdown("""
        Temporiq AI is a clinical operations observation tool for tracking patient or process workflows in real-time. 
        Log timestamps, visualize progress, and use AI-powered analysis to find bottlenecks.

        *Built by [Sunny Patel](https://github.com/srpatel03), Senior Data Analyst, for clinical operations teams.*
        
        ---
        Please log in or sign up to continue.
        """)
        login_tab, signup_tab = st.tabs(["Login", "Sign Up"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login")

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        try:
                            user = AuthDB.sign_in(email, password)
                            if user:
                                st.session_state.user = user
                                st.rerun()
                            else:
                                st.error("Login failed. Please check your credentials.")
                        except Exception as e:
                            st.error(str(e))
            if st.button("Forgot password?", key="forgot_password_btn"):
                st.session_state.show_forgot_password = True
                st.rerun()

        with signup_tab:
            with st.form("signup_form"):
                email = st.text_input("Email", key="signup_email")
                password = st.text_input("Password", type="password", key="signup_password")
                submitted = st.form_submit_button("Sign Up")

                if submitted:
                    if not email or not password:
                        st.error("Please enter both email and password.")
                    else:
                        try:
                            user = AuthDB.sign_up(email, password)
                            st.success("Sign up successful! Please go to the Login tab to continue.")
                        except Exception as e:
                            if "User already registered" in str(e):
                                st.error("An account with this email already exists. Please sign in or use 'Forgot password?'.")
                            else:
                                st.error(str(e))