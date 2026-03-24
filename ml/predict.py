import joblib
import os
import json
import pandas as pd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_user(username):
    profile_path = os.path.join(BASE_DIR, "profiles", f"{username}.json")

    if not os.path.exists(profile_path):
        raise Exception("User not found")

    with open(profile_path) as f:
        profile = json.load(f)

    model = joblib.load(profile["model"])
    scaler = joblib.load(profile["scaler"])

    return model, scaler


def predict_anomaly(username, features):
    """
    features: list of numbers (dwell + flight)
    returns: "normal" or "intruder"
    """

    model, scaler = load_user(username)

    # Convert to DataFrame
    df = pd.DataFrame([features])

    # Scale using saved scaler
    X_scaled = scaler.transform(df)

    prediction = model.predict(X_scaled)

    if prediction[0] == 1:
        return "normal"
    else:
        return "intruder"