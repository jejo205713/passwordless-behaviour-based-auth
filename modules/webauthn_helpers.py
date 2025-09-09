# modules/webauthn_helpers.py

from webauthn import (
    generate_registration_options,
    generate_authentication_options,
)
from webauthn.helpers.structs import AuthenticatorSelectionCriteria
import base64

# --- Relying Party (RP) Configuration ---
# This identifies your web application to the browser and authenticator
RP_ID = "localhost"
RP_NAME = "AdaptiveAuth Demo"
ORIGIN = f"http://{RP_ID}:8501"

def get_registration_options(email: str) -> dict:
    """
    Generates the options for WebAuthn registration and returns them
    as a simple, JSON-serializable dictionary.
    """
    # Create an instance of the required class for authenticator selection.
    auth_selection = AuthenticatorSelectionCriteria(
        authenticator_attachment="platform",
        user_verification="preferred",
    )

    # Call the library function to get its special class object
    options_obj = generate_registration_options(
        rp_id=RP_ID,
        rp_name=RP_NAME,
        user_id=email.encode('utf-8'),
        user_name=email,
        authenticator_selection=auth_selection,
    )

    # Manually create a clean dictionary from the object's attributes.
    # This ensures it can be perfectly converted to JSON for the frontend.
    options_dict = {
        "rp": {
            "name": options_obj.rp.name,
            "id": options_obj.rp.id,
        },
        "user": {
            "id": base64.urlsafe_b64encode(options_obj.user.id).decode('utf-8').rstrip("="),
            "name": options_obj.user.name,
            "displayName": options_obj.user.display_name,
        },
        "challenge": base64.urlsafe_b64encode(options_obj.challenge).decode('utf-8').rstrip("="),
        "pubKeyCredParams": [
            {"type": param.type, "alg": param.alg} for param in options_obj.pub_key_cred_params
        ],
        "timeout": options_obj.timeout,
        "attestation": options_obj.attestation,
        "authenticatorSelection": {
            "authenticatorAttachment": options_obj.authenticator_selection.authenticator_attachment,
            "userVerification": options_obj.authenticator_selection.user_verification,
        },
    }

    return options_dict

def get_authentication_options(user_credential: dict) -> dict:
    """
    Generates the options for WebAuthn authentication (login) and returns them
    as a simple, JSON-serializable dictionary.
    """
    raw_id_str = user_credential.get("rawId")
    if not raw_id_str:
        raise ValueError("Credential is missing 'rawId'")
        
    padding = '=' * (-len(raw_id_str) % 4)
    decoded_credential_id = base64.urlsafe_b64decode(raw_id_str + padding)

    # It's good practice to also provide the credential type here.
    options_obj = generate_authentication_options(
        rp_id=RP_ID,
        allow_credentials=[{"id": decoded_credential_id, "type": "public-key"}],
    )

    # Manually build the clean dictionary
    options_dict = {
        "challenge": base64.urlsafe_b64encode(options_obj.challenge).decode('utf-8').rstrip("="),
        "timeout": options_obj.timeout,
        "rpId": options_obj.rp_id,
        "allowCredentials": [
            {
                "type": cred['type'],
                # --- THIS IS THE FIX ---
                # Changed 'base6d4' to the correct 'base64'.
                "id": base64.urlsafe_b64encode(cred['id']).decode('utf-8').rstrip("=")
            } for cred in options_obj.allow_credentials
        ],
    }

    return options_dict