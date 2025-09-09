# modules/auth_service.py

import random
import string
import math  # Make sure math is imported for the distance calculation
from . import user_manager, webauthn_helpers

# --- Passkey Generation (Unaltered from your code) ---
def generate_and_save_passkey(email: str) -> str:
    """
    Generates a simple, memorable passkey, saves it, and returns it.
    """
    words = ["moon", "star", "nova", "flare", "comet", "ocean", "river", "cloud"]
    word = random.choice(words)
    digits = "".join(random.choices(string.digits, k=3))
    passkey = f"{word}-{digits}"
    user_manager.save_secret_passkey(email, passkey)
    return passkey

# --- WebAuthn Verification (Unaltered from your code) ---
def verify_webauthn_registration(credential, expected_challenge: str) -> bool:
    """
    Verifies the registration credential received from the browser. (Placeholder)
    """
    return credential is not None and expected_challenge is not None

def verify_webauthn_authentication(email: str, login_credential, expected_challenge: str) -> bool:
    """
    Verifies the authentication credential received from the browser. (Placeholder)
    """
    return login_credential is not None and expected_challenge is not None


# --- THIS IS THE UPDATED FUNCTION ---
def verify_clicks(email: str, new_clicks: list) -> bool:
    """
    Verifies a user's click pattern using a tolerance radius to account for human error.
    This creates the "average circular round area" you described.
    
    Args:
        email (str): The user's email.
        new_clicks (list): A list of {x, y} dicts from the new login attempt.

    Returns:
        bool: True if the pattern matches within the tolerance, False otherwise.
    """
    # Define the radius of the acceptable "circular area" in pixels.
    # A value of 35 is a good starting point for marginal error.
    TOLERANCE_RADIUS = 35

    baseline_clicks = user_manager.get_click_profile(email)

    # Add robust validation to prevent crashes if data is missing or malformed.
    if not baseline_clicks or not isinstance(baseline_clicks, list) or len(baseline_clicks) != 3:
        print(f"Verification failed: Baseline clicks for {email} are missing or invalid.")
        return False
    if not new_clicks or not isinstance(new_clicks, list) or len(new_clicks) != 3:
        print(f"Verification failed: New click attempt is missing or invalid.")
        return False

    # Iterate through each of the three points, comparing the baseline to the new attempt.
    for i, (baseline_point, new_point) in enumerate(zip(baseline_clicks, new_clicks)):
        # Calculate the Euclidean distance between the saved point and the new point.
        # distance = sqrt((x2 - x1)^2 + (y2 - y1)^2)
        distance = math.sqrt(
            (baseline_point["x"] - new_point["x"])**2 + 
            (baseline_point["y"] - new_point["y"])**2
        )
        
        # If the distance is greater than our allowed tolerance, the check fails immediately.
        if distance > TOLERANCE_RADIUS:
            # This print statement is very helpful for debugging in your terminal
            print(f"Click verification for {email} FAILED on point #{i+1}. Distance was {distance:.1f}px (Max is {TOLERANCE_RADIUS}px).")
            return False
            
    # If the loop completes, it means all points were within the tolerance radius.
    print(f"Click verification for {email} SUCCEEDED.")
    return True


# --- Passkey Verification (Unaltered from your code) ---
def verify_passkey(email: str, attempt: str) -> bool:
    """
    Verifies a user's submitted passkey attempt. Case-insensitive and strips whitespace.
    """
    correct_passkey = user_manager.get_secret_passkey(email)
    if not correct_passkey:
        return False
    
    return attempt.strip().lower() == correct_passkey.lower()