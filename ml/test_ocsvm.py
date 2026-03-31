import pandas as pd
import joblibdie
import os
from sklearn.preprocessing import StandardScaler

def main():
    print("Testing One-Class SVM...")

    # Paths
    current_file = os.path.abspath(__file__)
    base_dir = os.path.dirname(current_file)

    data_path = os.path.join(base_dir, "data", "processed", "features.csv")
    model_path = os.path.join(base_dir, "saved_models", "ocsvm_model.pkl")

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

    # Normalize
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Predict
    prediction = model.predict(X_scaled)

    if prediction[0] == 1:
        print("\nResult: NORMAL USER ✅")
    else:
        print("\nResult: INTRUSION DETECTED ❌")

if __name__ == "__main__":
    main()