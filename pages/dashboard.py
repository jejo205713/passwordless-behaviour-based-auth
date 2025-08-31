# C:\Users\Jejo\Documents\passwordless-behaviour-based-auth-main\pages\dashboard.py

import streamlit as st

st.set_page_config(page_title="Dashboard", page_icon="📊")

# Verify authentication status from the session state
if st.session_state.get('is_authenticated', False):
    st.title(f"Welcome, {st.session_state.get('user_email', 'User')}!")
    st.header("Secure Dashboard")
    st.success("You have been successfully authenticated with both fingerprint and behavioral biometrics.")

    st.markdown("---")
    st.subheader("Your Account Details")
    st.metric(label="Account Balance", value="$25,789.43", delta="+$523.12")
    st.metric(label="Security Threat Level", value="Low")

    st.write("This is a protected area. Only users who pass both security checks can see this content.")

else:
    st.title("🚫 Access Denied")
    st.error("You are not authenticated. Please return to the login page to proceed.")
    
    # --- THE FIX IS HERE ---
    # The path now correctly points to your "login.py" file.
    st.page_link("pages/login.py", label="Go to Login", icon="🔑")
    # -----------------------