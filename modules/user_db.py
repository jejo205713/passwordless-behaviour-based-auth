# C:\Users\Jejo\Documents\passwordless-behaviour-based-auth-main\modules\user_db.py

import math
import random

# In-memory dictionary to simulate a real database for the hackathon.
USER_DATABASE = {}

def generate_secret_passkey() -> str:
    """Generates a simple, memorable passkey for the user."""
    words = ["apple", "river", "mountain", "ocean", "sun", "moon", "star", "forest", "fire", "ice"]
    chosen_word = random.choice(words)
    number = random.randint(100, 999)
    return f"{chosen_word}-{number}"

def create_user_profile(email: str):
    """Creates a new, empty profile entry for a user."""
    if email not in USER_DATABASE:
        USER_DATABASE[email] = {
            "baseline_speeds": [],
            "average_speed": None,
            "click_profile": [],
            "secret_passkey": None,
        }
    print(f"Current DB state: {USER_DATABASE}")

def add_baseline_speed(email: str, speed: float):
    if email in USER_DATABASE:
        USER_DATABASE[email]["baseline_speeds"].append(speed)

def calculate_and_save_average_speed(email: str):
    if email in USER_DATABASE and USER_DATABASE[email]["baseline_speeds"]:
        speeds = USER_DATABASE[email]["baseline_speeds"]
        avg = sum(speeds) / len(speeds)
        USER_DATABASE[email]["average_speed"] = avg

def get_user_average_speed(email: str) -> float | None:
    if email in USER_DATABASE:
        return USER_DATABASE[email]["average_speed"]
    return None

def save_click_profile(email: str, clicks: list):
    if email in USER_DATABASE:
        USER_DATABASE[email]["click_profile"] = [{"x": c["left"], "y": c["top"]} for c in clicks]

def get_click_profile(email: str) -> list | None:
    if email in USER_DATABASE:
        return USER_DATABASE[email]["click_profile"]
    return None

def verify_clicks(baseline_clicks: list, new_clicks: list, tolerance: int = 25) -> bool:
    if len(baseline_clicks) != len(new_clicks):
        return False
    for baseline_pt, new_pt in zip(baseline_clicks, new_clicks):
        distance = math.sqrt((baseline_pt["x"] - new_pt["x"])**2 + (baseline_pt["y"] - new_pt["y"])**2)
        if distance > tolerance:
            return False
    return True

def save_secret_passkey(email: str, passkey: str):
    """Saves the user's secret passkey."""
    if email in USER_DATABASE:
        USER_DATABASE[email]["secret_passkey"] = passkey
    print(f"Current DB state: {USER_DATABASE}")

def verify_secret_passkey(email: str, attempt: str) -> bool:
    """Checks if the provided passkey attempt is correct."""
    if email in USER_DATABASE:
        # .strip() removes accidental spaces, .lower() makes it case-insensitive
        return USER_DATABASE[email]["secret_passkey"] == attempt.strip().lower()
    return False