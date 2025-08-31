# C:\Users\Jejo\Documents\passwordless-behaviour-based-auth-main\pages\login.py

import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from modules import auth_logic, user_db
import time
import os
import json
from streamlit.components.v1 import html  # <-- THIS IS THE MISSING LINE THAT FIXES THE ERROR

st.set_page_config(page_title="Login", page_icon="👆")

# --- Session State Initialization ---
if 'page_mode' not in st.session_state:
    st.session_state.page_mode = "login"
if 'flow_step' not in st.session_state:
    st.session_state.flow_step = "start"
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'baseline_attempts' not in st.session_state:
    st.session_state.baseline_attempts = 3
if 'start_time' not in st.session_state:
    st.session_state.start_time = 0

challenge_text = "the quick brown fox jumps over the lazy dog"
bg_image_path = "background.jpeg"
try:
    bg_image = Image.open(bg_image_path)
except FileNotFoundError:
    st.warning("`background.png` not found. Using a default background.")
    bg_image = Image.new('RGB', (704, 500), '#1E2A3A')


# JavaScript to trigger the WebAuthn API.
def trigger_webauthn_prompt(options):
    js_code = f"""
    <script>
    const options = {json.dumps(options)};
    function base64urlToBuffer(base64url) {{
        const base64 = base64url.replace(/-/g, '+').replace(/_/g, '/');
        const binStr = atob(base64);
        const bin = new Uint8Array(binStr.length);
        for (let i = 0; i < binStr.length; i++) {{
            bin[i] = binStr.charCodeAt(i);
        }}
        return bin.buffer;
    }}
    options.challenge = base64urlToBuffer(options.challenge);
    options.user.id = base64urlToBuffer(options.user.id);

    navigator.credentials.create({{ publicKey: options }})
        .then(credential => {{
            alert("✅ Fingerprint Registered/Verified Successfully!");
        }})
        .catch(error => {{
            console.error("WebAuthn Error:", error);
            alert("❌ Fingerprint failed. Make sure you have a fingerprint reader and enable it for this site.");
        }});
    </script>
    """
    html(js_code, height=50)


# ==============================================================================
# --- LOGIN VIEW ---
# ==============================================================================
if st.session_state.page_mode == "login":
    st.title("Adaptive Behavioral Login")

    if st.session_state.flow_step == "start":
        email = st.text_input("Enter your registered email", key="login_email")
        if st.button("Login with Fingerprint", type="primary"):
            if email and user_db.get_user_average_speed(email) is not None:
                st.session_state.user_email = email
                st.session_state.flow_step = "awaiting_fingerprint_login"
                st.rerun()
            else:
                st.error("User not found. Please register first.")
        st.divider()
        if st.button("New user? Register here"):
            st.session_state.page_mode = "register"
            st.session_state.flow_step = "register_email"
            st.rerun()

    elif st.session_state.flow_step == "awaiting_fingerprint_login":
        st.header("Step 1: Fingerprint Verification")
        st.info("Your browser will now ask for your fingerprint.")
        options, _ = auth_logic.get_registration_options(st.session_state.user_email)
        trigger_webauthn_prompt(options)
        
        if st.button("Continue to Image Challenge"):
            st.session_state.flow_step = "verify_clicks"
            st.rerun()

    elif st.session_state.flow_step == "verify_clicks":
        st.header("Step 2: Image Clicks")
        st.info("Please click your 3 secret points in the correct order.")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color="#FFA500",
            background_image=bg_image, drawing_mode="point", key="canvas_verify"
        )
        if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) == 3:
            baseline_clicks = user_db.get_click_profile(st.session_state.user_email)
            new_clicks = [{"x": c["left"], "y": c["top"]} for c in canvas_result.json_data["objects"]]
            if user_db.verify_clicks(baseline_clicks, new_clicks):
                st.success("✅ Click profile MATCHED. Access Granted!")
                st.balloons()
                st.session_state.is_authenticated = True
                time.sleep(1)
                st.switch_page("pages/dashboard.py")
            else:
                st.warning("⚠️ Click pattern was incorrect. Please complete the recovery challenge.")
                st.session_state.flow_step = "step_up_challenge"
                st.session_state.start_time = time.time()
                time.sleep(2)
                st.rerun()

    elif st.session_state.flow_step == "step_up_challenge":
        st.header("Step-Up Challenge")
        st.info("As an extra security step, please complete BOTH challenges below.")
        user_input_typing = st.text_input(f"1. Type '{challenge_text}'", key="v_t_challenge")
        user_input_passkey = st.text_input("2. Enter your Secret Passkey", key="v_p_challenge")
        if st.button("Verify Recovery"):
            duration = time.time() - st.session_state.start_time
            user_avg = user_db.get_user_average_speed(st.session_state.user_email)
            lower_bound, upper_bound = user_avg * 0.60, user_avg * 1.40
            typing_correct = (user_input_typing == challenge_text) and (lower_bound <= duration <= upper_bound)
            passkey_correct = user_db.verify_secret_passkey(st.session_state.user_email, user_input_passkey)
            if typing_correct and passkey_correct:
                st.success("✅ Recovery successful! Access Granted!")
                st.balloons()
                st.session_state.is_authenticated = True
                time.sleep(1)
                st.switch_page("pages/dashboard.py")
            else:
                st.error("❌ Recovery information was incorrect. Access Denied.")
                st.session_state.flow_step = "start"
                time.sleep(3)
                st.rerun()


# ==============================================================================
# --- REGISTRATION VIEW ---
# ==============================================================================
elif st.session_state.page_mode == "register":
    st.title("New User Registration")

    if st.session_state.flow_step == "register_email":
        st.header("Step 1: Create Your Account")
        email = st.text_input("Enter your email", key="reg_email")
        if st.button("Create Account & Register Fingerprint"):
            if email:
                user_db.create_user_profile(email)
                st.session_state.user_email = email
                st.session_state.flow_step = "awaiting_fingerprint_register"
                st.rerun()
            else:
                st.warning("Please enter a valid email.")

    elif st.session_state.flow_step == "awaiting_fingerprint_register":
        st.header("Step 2: Register Fingerprint")
        st.info("Your browser will now ask for your fingerprint to register this device.")
        options, _ = auth_logic.get_registration_options(st.session_state.user_email)
        trigger_webauthn_prompt(options)

        if st.button("Continue to Profile Setup"):
            st.session_state.flow_step = "baseline_typing"
            st.session_state.start_time = time.time()
            st.rerun()

    elif st.session_state.flow_step == "baseline_typing":
        st.header(f"Step 3: Profile Setup (Typing) - {st.session_state.baseline_attempts} attempts left")
        user_input = st.text_input(f"Type '{challenge_text}'", key=f"b_t_{st.session_state.baseline_attempts}")
        if user_input == challenge_text:
            duration = time.time() - st.session_state.start_time
            user_db.add_baseline_speed(st.session_state.user_email, duration)
            st.success(f"Attempt recorded: {duration:.2f}s")
            st.session_state.baseline_attempts -= 1
            st.session_state.start_time = time.time()
            time.sleep(1)
            if st.session_state.baseline_attempts == 0:
                user_db.calculate_and_save_average_speed(st.session_state.user_email)
                st.session_state.flow_step = "baseline_clicks"
            st.rerun()

    elif st.session_state.flow_step == "baseline_clicks":
        st.header("Step 4: Profile Setup (Clicks)")
        st.info("Click 3 distinct, memorable points on the image.")
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)", stroke_width=3, stroke_color="#FFA500",
            background_image=bg_image, drawing_mode="point", key="canvas_baseline"
        )
        if canvas_result.json_data is not None and len(canvas_result.json_data["objects"]) == 3:
            if st.button("Save Click Profile"):
                user_db.save_click_profile(st.session_state.user_email, canvas_result.json_data["objects"])
                passkey = user_db.generate_secret_passkey()
                user_db.save_secret_passkey(st.session_state.user_email, passkey)
                st.session_state.passkey = passkey
                st.session_state.flow_step = "show_passkey"
                st.rerun()

    elif st.session_state.flow_step == "show_passkey":
        st.header("IMPORTANT: Save Your Secret Passkey!")
        st.warning("This is the ONLY way to recover your account. Store it somewhere safe.")
        st.code(st.session_state.passkey)
        if st.button("I have saved my passkey. Finish Registration."):
            st.success("✅ Registration complete! You can now log in.")
            st.session_state.page_mode = "login"
            st.session_state.flow_step = "start"
            time.sleep(2)
            st.rerun()

    if st.session_state.flow_step != "register_email":
        if st.button("<< Back to Login"):
            st.session_state.page_mode = "login"
            st.session_state.flow_step = "start"
            st.rerun()