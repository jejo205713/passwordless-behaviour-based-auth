# passwordless_auth_app/modules/behavioral_analyzer.py

import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'behavioral_model.pkl')

try:
    MODEL = joblib.load(MODEL_PATH)
except FileNotFoundError:
    MODEL = None
    print(f"Warning: Model file not found at {MODEL_PATH}. The analyzer will deny all requests.")
    print("Please run 'python models/train_model.py' to generate the model.")

def extract_features(data: dict) -> np.ndarray:
    """
    Converts raw behavioral data into a feature vector for the model.
    For this demo, we only use typing duration. A real system would use many more features.
    """
    # Use a default value if 'typing_duration' is missing
    duration = data.get('typing_duration', 15.0) 
    # The model expects a 2D array, so we reshape it: [[value]]
    return np.array([[duration]])

def analyze_behavior(data: dict) -> str:
    """
    Analyzes the behavioral feature vector using the pre-trained model.
    Returns a decision: 'Grant' or 'Deny'.
    """
    if MODEL is None:
        return "Deny"  # Fail-safe: if the model isn't loaded, deny access.

    features = extract_features(data)
    
    # The One-Class SVM predicts:
    #  1 for an "inlier" (normal, trusted behavior)
    # -1 for an "outlier" (anomalous, untrusted behavior)
    prediction = MODEL.predict(features)

    if prediction[0] == 1:
        return "Grant"
    else:
        return "Deny"
