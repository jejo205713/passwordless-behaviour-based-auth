# passwordless_auth_app/models/train_model.py

import pandas as pd
from sklearn.svm import OneClassSVM
import joblib
import os

print("Starting model training process...")

# Define the path to save the model
output_dir = os.path.dirname(__file__)
model_path = os.path.join(output_dir, 'behavioral_model.pkl')
data_path = os.path.join(output_dir, '..', 'data', 'sample_sessions.csv')

# 1. Load data
# We'll use the sample CSV file.
try:
    df = pd.read_csv(data_path)
    print(f"Successfully loaded data from '{data_path}'")
except FileNotFoundError:
    print(f"Data file not found at '{data_path}'. Using hardcoded default data.")
    # Fallback to hardcoded data if CSV is missing
    normal_behavior = {'typing_duration': [4.5, 5.1, 6.2, 7.3, 5.5, 6.8, 5.9, 6.5]}
    df = pd.DataFrame(normal_behavior)

# 2. Prepare data for the model
# We are only using 'typing_duration' as a feature.
X = df[['typing_duration']]
print("Training data features:\n", X)

# 3. Initialize and Train the One-Class SVM model
# 'nu' is a key parameter: it's an upper bound on the fraction of training errors
# and a lower bound of the fraction of support vectors. Essentially, it controls
# the trade-off between finding all normal points and misclassifying some.
ocsvm = OneClassSVM(kernel='rbf', gamma='auto', nu=0.05)
ocsvm.fit(X)

# 4. Save the trained model to a file
joblib.dump(ocsvm, model_path)

print("-" * 30)
print(f"✅ Model training complete.")
print(f"Model saved to: '{model_path}'")
print("You can now run the Streamlit web application.")
