import pandas as pd
import os
import joblib
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import json

def main():
    username = input("Enter username: ")

    print("Type the phrase 'greyc laboratory' 5 times (use your dataset instead for now)")

    # Load dataset (for now simulate registration using dataset)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "processed", "features.csv")

    df = pd.read_csv(data_path)

    # Filter user data
    user_data = df[df["subject"] == df["subject"].unique()[0]]

    X = user_data.select_dtypes(include=["number"])

    # Scale
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Train model
    model = OneClassSVM(gamma='auto')
    model.fit(X_scaled)

    # Save model + scaler
    model_path = os.path.join(base_dir, "models", f"{username}_model.pkl")
    scaler_path = os.path.join(base_dir, "models", f"{username}_scaler.pkl")

    joblib.dump(model, model_path)
    joblib.dump(scaler, scaler_path)

    # Save profile
    profile = {
        "username": username,
        "model": model_path,
        "scaler": scaler_path
    }

    profile_path = os.path.join(base_dir, "profiles", f"{username}.json")

    with open(profile_path, "w") as f:
        json.dump(profile, f)

    print("User registered successfully!")

if __name__ == "__main__":
    main()