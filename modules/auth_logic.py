# passwordless_auth_app/modules/auth_logic.py

from webauthn import generate_registration_options
from webauthn.helpers.structs import AuthenticatorSelectionCriteria
import base64

# --- Configuration ---
RP_ID = "localhost"
RP_NAME = "Behavioral Auth Demo App"
ORIGIN = f"http://{RP_ID}:8501"

def get_registration_options(email: str) -> (dict, str):
    """
    Generate WebAuthn registration options and manually construct the
    dictionary for the frontend to bypass all internal library bugs.
    """
    options_object = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=email.encode("utf-8"),
        user_name=email,
        authenticator_selection=AuthenticatorSelectionCriteria(
            authenticator_attachment="platform",
            user_verification="preferred",
        )
    )

    # --- THE FINAL, CORRECTED FIX: MANUAL DICTIONARY CREATION ---
    # We build the dictionary ourselves, treating each attribute
    # according to its actual type (string or Enum).

    challenge_bytes = options_object.challenge
    user_id_bytes = options_object.user.id

    options_dict = {
        "rp": {
            "id": options_object.rp.id,
            "name": options_object.rp.name,
        },
        "user": {
            "id": base64.urlsafe_b64encode(user_id_bytes).decode('utf-8').rstrip("="),
            "name": options_object.user.name,
            "displayName": options_object.user.display_name,
        },
        "challenge": base64.urlsafe_b64encode(challenge_bytes).decode('utf-8').rstrip("="),
        "pubKeyCredParams": [
            {"type": "public-key", "alg": param.alg.value} for param in options_object.pub_key_cred_params
        ],
        "timeout": options_object.timeout,
        
        # --- THE FIX IS HERE: These are already strings, so we remove `.value` ---
        "attestation": options_object.attestation,
        "authenticatorSelection": {
            "authenticatorAttachment": options_object.authenticator_selection.authenticator_attachment,
            "userVerification": options_object.authenticator_selection.user_verification,
        },
        # --------------------------------------------------------------------------
    }

    challenge_str = options_dict["challenge"]

    return options_dict, challenge_str
