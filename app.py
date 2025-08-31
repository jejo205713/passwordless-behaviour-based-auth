# passwordless_auth_app/app.py

import streamlit as st

st.set_page_config(
    page_title="Passwordless Auth Demo",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("Welcome to the Future of Authentication")

st.markdown(
    """
    This application demonstrates a two-factor authentication system combining:
    1.  **Passwordless Login**: Using your device's fingerprint via the WebAuthn API.
    2.  **Behavioral Biometrics**: Analyzing your typing pattern as a second layer of security.

    **Please navigate to the `Login` page from the sidebar to begin.**
    """
)

st.info("👈 Select a page from the sidebar to get started.")
