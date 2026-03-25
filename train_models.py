#!/usr/bin/env python3
"""
KeyGuard ML Model Training Script
Trains Random Forest and One-Class SVM models using keystroke data
"""

import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
import warnings

warnings.filterwarnings('ignore')

# Get base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "ml", "data", "processed", "features.csv")
MODELS_DIR = os.path.join(BASE_DIR, "ml", "saved_models")
RF_MODEL_PATH = os.path.join(MODELS_DIR, "rf_model.pkl")
SVM_MODEL_PATH = os.path.join(MODELS_DIR, "svm_model.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler.pkl")

# Also save to backend models directory for compatibility
BACKEND_MODELS_DIR = os.path.join(BASE_DIR, "backend", "models")
BACKEND_RF_PATH = os.path.join(BACKEND_MODELS_DIR, "random_forest_model.pkl")
BACKEND_SVM_PATH = os.path.join(BACKEND_MODELS_DIR, "one_class_svm_model.pkl")
BACKEND_SCALER_PATH = os.path.join(BACKEND_MODELS_DIR, "scaler.pkl")

def create_directories():
    """Create necessary directories"""
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(BACKEND_MODELS_DIR, exist_ok=True)
    print("✓ Directories created")

def load_data():
    """Load keystroke features from CSV"""
    if not os.path.exists(DATA_PATH):
        print(f"✗ Data file not found: {DATA_PATH}")
        sys.exit(1)
    
    print(f"Loading data from: {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)
    print(f"✓ Data loaded: {df.shape[0]} samples, {df.shape[1]} columns")
    
    # Display basic info
    print(f"  Columns: {list(df.columns[:10])}...")
    print(f"  First 3 rows of subjects: {df['subject'].head(3).tolist()}")
    
    return df

def prepare_features(df):
    """Prepare features for training"""
    print("\nPreparing features...")
    
    # Extract only numeric columns (keystroke timing features)
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Remove 'subject' if it's numeric (it shouldn't be used as feature)
    if 'subject' in numeric_cols:
        numeric_cols.remove('subject')
    
    X = df[numeric_cols].copy()
    y = df['subject'].copy()
    
    # Handle missing values
    X = X.fillna(X.mean())
    
    # Remove rows with NaN in y
    valid_idx = y.notna()
    X = X[valid_idx]
    y = y[valid_idx]
    
    print(f"✓ Features prepared: {X.shape[0]} samples, {X.shape[1]} features")
    print(f"  Feature names: {numeric_cols[:5]}...")
    print(f"  Classes: {y.unique()}")
    print(f"  Class distribution: {y.value_counts().to_dict()}")
    
    return X, y, numeric_cols

def train_random_forest(X_train, X_test, y_train, y_test):
    """Train Random Forest classifier"""
    print("\n" + "="*60)
    print("TRAINING RANDOM FOREST")
    print("="*60)
    
    print("Training Random Forest with 100 estimators...")
    rf_model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,
        verbose=1
    )
    
    rf_model.fit(X_train, y_train)
    print("✓ Random Forest trained")
    
    # Evaluate
    print("\nEvaluating on test set...")
    y_pred = rf_model.predict(X_test)
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print(f"\nRandom Forest Metrics:")
    print(f"  Accuracy:  {accuracy:.4f} ({accuracy*100:.2f}%)")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall:    {recall:.4f}")
    print(f"  F1-Score:  {f1:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': X_train.columns,
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTop 10 Most Important Features:")
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['feature']}: {row['importance']:.4f}")
    
    return rf_model

def train_one_class_svm(X_train, X_test, y_train, y_test, scaler):
    """Train One-Class SVM for anomaly detection"""
    print("\n" + "="*60)
    print("TRAINING ONE-CLASS SVM")
    print("="*60)
    
    # Scale features for SVM
    print("Scaling features for SVM...")
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    print("✓ Features scaled")
    
    # Train One-Class SVM on normal user data (subject 1)
    print("\nTraining One-Class SVM (anomaly detection)...")
    svm_model = OneClassSVM(kernel='rbf', gamma='auto', nu=0.05)
    svm_model.fit(X_train_scaled)
    print("✓ One-Class SVM trained")
    
    # Evaluate
    print("\nEvaluating on test set...")
    y_pred_svm = svm_model.predict(X_test_scaled)  # Returns 1 for inliers, -1 for outliers
    
    # Calculate metrics
    # Convert predictions: 1 = normal, -1 = anomaly
    accuracy_svm = accuracy_score(y_test.map(lambda x: 1 if x == 1 else -1), y_pred_svm)
    
    print(f"\nOne-Class SVM Metrics:")
    print(f"  Accuracy: {accuracy_svm:.4f} ({accuracy_svm*100:.2f}%)")
    print(f"  Normal samples detected: {(y_pred_svm == 1).sum()} / {len(y_pred_svm)}")
    print(f"  Anomalies detected: {(y_pred_svm == -1).sum()} / {len(y_pred_svm)}")
    
    return svm_model

def save_models(rf_model, svm_model, scaler):
    """Save trained models"""
    print("\n" + "="*60)
    print("SAVING MODELS")
    print("="*60)
    
    # Save to ml/saved_models
    joblib.dump(rf_model, RF_MODEL_PATH)
    print(f"✓ Random Forest saved: {RF_MODEL_PATH}")
    
    joblib.dump(svm_model, SVM_MODEL_PATH)
    print(f"✓ One-Class SVM saved: {SVM_MODEL_PATH}")
    
    joblib.dump(scaler, SCALER_PATH)
    print(f"✓ Scaler saved: {SCALER_PATH}")
    
    # Also save to backend models directory
    joblib.dump(rf_model, BACKEND_RF_PATH)
    print(f"✓ Random Forest saved: {BACKEND_RF_PATH}")
    
    joblib.dump(svm_model, BACKEND_SVM_PATH)
    print(f"✓ One-Class SVM saved: {BACKEND_SVM_PATH}")
    
    joblib.dump(scaler, BACKEND_SCALER_PATH)
    print(f"✓ Scaler saved: {BACKEND_SCALER_PATH}")

def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("KEYGUARD ML MODEL TRAINING")
    print("="*60)
    
    # Step 1: Create directories
    create_directories()
    
    # Step 2: Load data
    df = load_data()
    
    # Step 3: Prepare features
    X, y, numeric_cols = prepare_features(df)
    
    # Step 4: Split data
    print(f"\nSplitting data (80/20 train/test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print(f"✓ Training set: {X_train.shape[0]} samples")
    print(f"✓ Test set: {X_test.shape[0]} samples")
    
    # Step 5: Initialize scaler
    scaler = StandardScaler()
    
    # Step 6: Train Random Forest
    rf_model = train_random_forest(X_train, X_test, y_train, y_test)
    
    # Step 7: Train One-Class SVM
    svm_model = train_one_class_svm(X_train, X_test, y_train, y_test, scaler)
    
    # Step 8: Save models
    save_models(rf_model, svm_model, scaler)
    
    print("\n" + "="*60)
    print("✓ TRAINING COMPLETE!")
    print("="*60)
    print(f"\nModels saved to:")
    print(f"  - ML Directory: {MODELS_DIR}")
    print(f"  - Backend Directory: {BACKEND_MODELS_DIR}")
    print(f"\nYou can now use these models in the KeyGuard backend!")
    print("Restart the backend server to use the trained models.")

if __name__ == "__main__":
    main()
