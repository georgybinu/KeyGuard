"""
Configuration settings for KeyGuard backend
"""
import os

def _normalize_database_url(url: str) -> str:
    """Normalize provider-specific database URLs for SQLAlchemy."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg2://", 1)
    return url

# Model thresholds
NORMAL_THRESHOLD = 0.7  # RF probability threshold for normal behavior
SUSPICIOUS_THRESHOLD = 0.4  # Between suspicious and intrusion
ANOMALY_SCORE_THRESHOLD = -0.5  # One-Class SVM anomaly threshold

# Feature extraction parameters
DWELL_TIME_THRESHOLD = 50  # ms - time key is held down
FLIGHT_TIME_THRESHOLD = 100  # ms - time between key releases and next press

# Base paths
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODELS_DIR = os.path.join(BACKEND_DIR, "models")

# Database
DEFAULT_DATABASE_PATH = os.path.join(BACKEND_DIR, "keyguard.db")
DATABASE_URL = _normalize_database_url(os.getenv("DATABASE_URL", f"sqlite:///{DEFAULT_DATABASE_PATH}"))
IS_SQLITE = DATABASE_URL.startswith("sqlite")

# Frontend / deployment
CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if origin.strip()
]

# Model paths
MODEL_PATHS = {
    "random_forest": os.getenv("RF_MODEL_PATH", os.path.join(DEFAULT_MODELS_DIR, "random_forest_model.pkl")),
    "one_class_svm": os.getenv("SVM_MODEL_PATH", os.path.join(DEFAULT_MODELS_DIR, "one_class_svm_model.pkl")),
    "scaler": os.getenv("SCALER_PATH", os.path.join(DEFAULT_MODELS_DIR, "scaler.pkl")),
}

# Feature names expected by models
FEATURE_NAMES = [
    "dwell_time",
    "flight_time",
    "key_press_rate",
    "key_release_interval",
    "typing_speed",
]

# Training program
PHRASE_TRAINING_ROUNDS = 10
PARAGRAPH_TRAINING_ROUNDS = 3
TOTAL_TRAINING_ROUNDS = PHRASE_TRAINING_ROUNDS + PARAGRAPH_TRAINING_ROUNDS

# Keys that add noise for live authentication decisions
NOISY_KEYS = {
    " ",
    "Shift",
    "Backspace",
    "CapsLock",
    "Tab",
    "Enter",
}

# Decision logic labels
DECISION_LABELS = {
    "normal": "normal",
    "suspicious": "suspicious",
    "intrusion": "intrusion",
}

# Logging
LOG_DIR = os.getenv("LOG_DIR", "./logs")
os.makedirs(LOG_DIR, exist_ok=True)
