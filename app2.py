# passwordless_auth_app/app.py

import streamlit as st
import os
import json
import random
import string

# ------------------------------
# JSON DB Setup
# ------------------------------
DB_PATH = r"C:\Users\Jejo\Documents\passwordless-behaviour-based-auth-main\data\users.json"

def init_db():
    """Make sure the users.json file exists and is valid."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    if not os.path.exists(DB_PATH):
        with open(DB_PATH, "w") as f:
            json.dump({}, f)  # start with empty dict
    else:
        # If file exists but is empty or invalid, reset it
        try:
            with open(DB_PATH, "r") as f:
                json.load(f)
        except (json.JSONDecodeError, ValueError):
            with open(DB_PATH, "w") as f:
                json.dump({}, f)

def load_users():
    try:
        with open(DB_PATH, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return {}  # fallback empty dict

def save_users(users):
    with open(DB_PATH, "w") as f:
        json.dump(users, f, indent=4)

def save_user(email, baseline_speeds, average_speed, click_profile, secret_passkey):
    users = load_users()
    users[email] = {
        "baseline_speeds": baseline_speeds,
        "average_speed": average_speed,
        "click_profile": click_profile,
        "secret_passkey": secret_passkey
    }
    save_users(users)

def get_user(email):
    users = load_users()
    return users.get(email)

# ------------------------------
# Helpers
# ------------------------------
def generate_safety_passkey():
    word = random.choice(["moon", "star", "nova", "flare", "comet", "ocean"])
    digits = ''.join(random.choices(string.digits, k=3))
    return f"{word}-{digits}"

# ------------------------------
# Streamlit Config
# ------------------------------
st.set_page_config(
    page_title="Passwordless Auth Demo",
    page_icon="🔒",
    layout="centered",
    initial_sidebar_state="auto",
)

init_db()

# ------------------------------
# Pages
# ------------------------------
def home():
    st.title("Welcome to the Future of Authentication 🔒")
    st.markdown(
        """
        This demo shows **multi-layered, passwordless authentication** with:
        - Fingerprint (WebAuthn API)
        - Image-point selection
        - Typing behavior analysis
        - Emergency passkey + OTP
        """
    )
    st.info("👉 Use sidebar to Register or Login.")

def register():
    st.header("📝 User Registration")
    email = st.text_input("Enter your Email")

    if st.button("Complete Registration"):
        if email:
            baseline_speeds = [random.uniform(8, 12) for _ in range(3)]
            avg_speed = sum(baseline_speeds) / len(baseline_speeds)
            click_profile = [{"x": 278.5, "y": 45}, {"x": 61.5, "y": 212}, {"x": 501.5, "y": 210}]
            secret_passkey = generate_safety_passkey()

            save_user(email, baseline_speeds, avg_speed, click_profile, secret_passkey)

            st.success(f"✅ Registration complete for {email}")
            st.info(f"⚠️ Your safety passkey is: **{secret_passkey}** (store it safely!)")
        else:
            st.error("Please enter your email before registering.")

def login():
    st.header("🔑 User Login")
    email = st.text_input("Enter your Email")

    if st.button("Check User"):
        user = get_user(email)
        if user:
            st.success(f"User found: {email}")
            st.json(user)  # Show stored data
        else:
            st.error("User not found! Please register first.")

def dashboard():
    st.title("📊 User Dashboard")
    st.success("You are securely logged in!")
    st.write("Welcome to your account.")

# ------------------------------
# Sidebar Navigation
# ------------------------------
pages = {
    "Home": home,
    "Register": register,
    "Login": login,
    "Dashboard": dashboard,
}

choice = st.sidebar.radio("Navigate", list(pages.keys()))
pages[choice]()
