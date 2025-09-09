# modules/user_manager.py

import pandas as pd
import json
import os
from flask import current_app

def _get_db_path():
    return current_app.config['USER_DB_PATH']

def _load_df():
    """
    Loads user data into a pandas DataFrame.
    Handles cases where the file doesn't exist or is empty.
    """
    path = _get_db_path()
    
    # --- THIS IS THE FIX ---
    # We check if the file doesn't exist OR if it exists but is empty.
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        # If either is true, create a fresh DataFrame with the correct columns.
        df = pd.DataFrame(columns=[
            'email', 'webauthn_credential', 'click_profile', 
            'secret_passkey', 'typing_samples', 'typing_average'
        ])
        # Save it to create the file with headers
        df.to_csv(path, index=False)
        return df
        
    # If the file exists and is not empty, read it as usual.
    return pd.read_csv(path)

def _save_df(df):
    path = _get_db_path()
    df.to_csv(path, index=False)

def get_user(email):
    df = _load_df()
    user_row = df[df['email'] == email]
    if user_row.empty:
        return None
    user_dict = user_row.to_dict('records')[0]
    for key in ['webauthn_credential', 'click_profile', 'typing_samples']:
        if pd.notna(user_dict[key]):
            try:
                user_dict[key] = json.loads(user_dict[key])
            except (json.JSONDecodeError, TypeError):
                user_dict[key] = None
    return user_dict

def create_user_profile(email):
    df = _load_df()
    if email in df['email'].values:
        return False
    new_user = {
        'email': email,
        'webauthn_credential': None,
        'click_profile': json.dumps([]),
        'secret_passkey': None,
        'typing_samples': json.dumps([]),
        'typing_average': None
    }
    new_df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
    _save_df(new_df)
    return True

def _update_user_field(email, field, value):
    df = _load_df()
    user_index = df.index[df['email'] == email].tolist()
    if not user_index:
        return
    if isinstance(value, (dict, list)):
        value = json.dumps(value)
    df.loc[user_index[0], field] = value
    _save_df(df)

def save_webauthn_credential(email, credential):
    _update_user_field(email, 'webauthn_credential', credential)

def get_webauthn_credential(email):
    user = get_user(email)
    return user.get('webauthn_credential') if user else None

def save_click_profile(email, clicks):
    _update_user_field(email, 'click_profile', clicks)

def get_click_profile(email):
    user = get_user(email)
    return user.get('click_profile') if user else None

def save_secret_passkey(email, passkey):
    _update_user_field(email, 'secret_passkey', passkey)

def get_secret_passkey(email):
    user = get_user(email)
    return user.get('secret_passkey') if user else None

def get_typing_baseline(email):
    user = get_user(email)
    if not user:
        return None
    return {
        "samples": user.get('typing_samples', []),
        "average_speed": user.get('typing_average')
    }

def save_typing_average(email, avg_speed):
    """Saves the calculated average typing speed for a user."""
    _update_user_field(email, 'typing_average', avg_speed)