import pandas as pd
import os

def main():
    print("Starting feature extraction...")

    # Get correct base path
    current_file = os.path.abspath(__file__)
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))

    input_path = os.path.join(base_dir, "ml", "data", "raw", "greyc.csv")
    output_path = os.path.join(base_dir, "ml", "data", "processed", "features.csv")

    print("Looking for file at:", input_path)

    # Load dataset (FIX: tab-separated)
    df = pd.read_csv(input_path, sep="\t")

    print("Dataset loaded")
    print(df.head())
    print("Columns before processing:", df.columns)

    # Remove missing values
    df = df.dropna()

    # FIX: Rename Username → subject
    if "subject" not in df.columns:
        if "Username" in df.columns:
            df.rename(columns={"Username": "subject"}, inplace=True)

    print("Columns after processing:", df.columns)

    # Save processed dataset
    df.to_csv(output_path, index=False)

    print("Features saved successfully!")

if __name__ == "__main__":
    main()