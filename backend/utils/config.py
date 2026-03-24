"""
Configuration settings for KeyGuard backend
"""
import os
from typing import Dict, Any

# Model thresholds
NORMAL_THRESHOLD = 0.7  # RF probability threshold for normal behavior
SUSPICIOUS_THRESHOLD = 0.4  # Between suspicious and intrusion
ANOMALY_SCORE_THRESHOLD = -0.5  # One-Class SVM anomaly threshold

# Feature extraction parameters
DWELL_TIME_THRESHOLD = 50  # ms - time key is held down
FLIGHT_TIME_THRESHOLD = 100  # ms - time between key releases and next press

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./keyguard.db")

# Model paths
MODEL_PATHS = {
    "random_forest": os.getenv("RF_MODEL_PATH", "/models/random_forest_model.pkl"),
    "one_class_svm": os.getenv("SVM_MODEL_PATH", "/models/one_class_svm_model.pkl"),
    "scaler": os.getenv("SCALER_PATH", "/models/scaler.pkl"),
}

# Feature names expected by models
FEATURE_NAMES = [
    "dwell_time",
    "flight_time",
    "key_press_rate",
    "key_release_interval",
    "typing_speed",
]

# Decision logic labels
DECISION_LABELS = {
    "normal": "normal",
    "suspicious": "suspicious",
    "intrusion": "intrusion",
}

# Logging
LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)
