import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score
import joblib
import os

def main():
    print("Starting Random Forest training...")

    # Get correct base path
    current_file = os.path.abspath(__file__)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    data_path = os.path.join(base_dir, "ml", "data", "processed", "features.csv")
    model_path = os.path.join(base_dir, "ml", "saved_models", "rf_model.pkl")

    # Load dataset
    df = pd.read_csv(data_path)

    print("Dataset loaded")
    print("Columns:", df.columns)

    # Ensure subject column exists
    if "subject" not in df.columns:
        raise ValueError("ERROR: 'subject' column not found. Check feature extraction step.")

    # Separate labels
    y = df["subject"]

    # Keep ONLY numeric columns (FIX for your error)
    X = df.select_dtypes(include=["number"])

    print("Using numeric columns:", X.columns)

    # Train-test split
    print("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Train model
    print("Training model...")
    model = RandomForestClassifier(n_estimators=50)
    model.fit(X_train, y_train)

    print("Model trained")

    # Predictions
    y_pred = model.predict(X_test)

    # Metrics
    print("Accuracy:", accuracy_score(y_test, y_pred))
    print("Precision:", precision_score(y_test, y_pred, average="macro"))
    print("Recall:", recall_score(y_test, y_pred, average="macro"))

    # Save model
    joblib.dump(model, model_path)

    print("Model saved successfully!")

if __name__ == "__main__":
    main()