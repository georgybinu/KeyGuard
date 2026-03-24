import pandas as pd
import joblib
import os

def main():
    print("Testing Random Forest model...")

    # Paths
    current_file = os.path.abspath(__file__)
    base_dir = os.path.dirname(current_file)

    data_path = os.path.join(base_dir, "data", "processed", "features.csv")
    model_path = os.path.join(base_dir, "saved_models", "rf_model.pkl")

    # Load model
    model = joblib.load(model_path)
    print("Model loaded")

    # Load dataset
    df = pd.read_csv(data_path)

    # Take one sample
    sample = df.sample(1)

    print("\nSample input:")
    print(sample)

    # Remove label
    X = sample.select_dtypes(include=["number"])

    # Predict
    prediction = model.predict(X)

    print("\nPredicted user:", prediction[0])
    print("Actual user:", sample["subject"].values[0])

if __name__ == "__main__":
    main()