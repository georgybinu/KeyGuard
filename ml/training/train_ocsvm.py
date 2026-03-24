import pandas as pd
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
import joblib
import os

def main():
    print("Starting One-Class SVM training...")

    # Paths
    current_file = os.path.abspath(__file__)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    data_path = os.path.join(base_dir, "ml", "data", "processed", "features.csv")
    model_path = os.path.join(base_dir, "ml", "saved_models", "ocsvm_model.pkl")

    # Load dataset
    df = pd.read_csv(data_path)

    print("Dataset loaded")
    print("Columns:", df.columns)

    # Ensure subject exists
    if "subject" not in df.columns:
        raise ValueError("ERROR: 'subject' column not found")

    # Select ONE user (legitimate user)
    legit_user = df["subject"].unique()[0]
    print("Training on user:", legit_user)

    user_data = df[df["subject"] == legit_user]

    # Remove label column
    X = user_data.select_dtypes(include=["number"])

    print("Using numeric columns:", X.columns)

    # Normalize data
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    print("Training One-Class SVM...")

    # Train model
    model = OneClassSVM(gamma='auto')
    model.fit(X_scaled)

    # Save model
    joblib.dump(model, model_path)

    print("One-Class SVM model saved successfully!")

if __name__ == "__main__":
    main() 