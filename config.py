# config.py

import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-and-random-string-for-dev')
    
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # --- CHANGE THIS LINE ---
    # The database will now be a CSV file.
    USER_DB_PATH = os.path.join(BASE_DIR, 'data', 'users.csv')