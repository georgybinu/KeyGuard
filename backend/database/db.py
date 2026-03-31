"""
Database models for KeyGuard
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

try:
    from ..utils.config import DATABASE_URL, IS_SQLITE
except ImportError:
    from utils.config import DATABASE_URL, IS_SQLITE

Base = declarative_base()

# Database setup
engine_kwargs = {"pool_pre_ping": True}
if IS_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """User profile model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, nullable=True)
    password_hash = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    training_completed = Column(Boolean, default=False)
    training_rounds = Column(Integer, default=0)
    
class Session(Base):
    """User session model"""
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_token = Column(String, unique=True, index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class IntrusionLog(Base):
    """Intrusion event logging model"""
    __tablename__ = "intrusion_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    session_id = Column(Integer, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    detection_type = Column(String)  # "anomaly" or "classification"
    rf_probability = Column(Float)  # Random Forest probability
    svm_anomaly_score = Column(Float)  # SVM anomaly score
    decision = Column(String)  # "normal", "suspicious", "intrusion"
    keystroke_data = Column(String)  # JSON string of keystroke data
    
class BehaviorProfile(Base):
    """User behavior profile for baseline comparison"""
    __tablename__ = "behavior_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    feature_name = Column(String)
    mean_value = Column(Float)
    std_dev = Column(Float)
    updated_at = Column(DateTime, default=datetime.utcnow)

class TrainingSample(Base):
    """Fixed-length per-round training sample used for per-user anomaly detection."""
    __tablename__ = "training_samples"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    round_number = Column(Integer, nullable=False)
    sample_type = Column(String, nullable=False, default="phrase")
    phrase = Column(String, nullable=True)
    prompt_text = Column(String, nullable=True)
    typed_text = Column(String, nullable=True)
    keystroke_count = Column(Integer, nullable=False, default=0)
    feature_vector = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

def _ensure_sqlite_columns():
    """Backfill columns on existing SQLite databases without a full migration tool."""
    if not IS_SQLITE:
        return
    inspector = inspect(engine)
    if "users" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("users")}
        statements = []
        if "phone" not in columns:
            statements.append("ALTER TABLE users ADD COLUMN phone VARCHAR")
        if "password_hash" not in columns:
            statements.append("ALTER TABLE users ADD COLUMN password_hash VARCHAR")
        if "training_completed" not in columns:
            statements.append("ALTER TABLE users ADD COLUMN training_completed BOOLEAN DEFAULT 0")
        if "training_rounds" not in columns:
            statements.append("ALTER TABLE users ADD COLUMN training_rounds INTEGER DEFAULT 0")

        if statements:
            with engine.begin() as connection:
                for statement in statements:
                    connection.execute(text(statement))

    if "training_samples" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("training_samples")}
        statements = []
        if "sample_type" not in columns:
            statements.append("ALTER TABLE training_samples ADD COLUMN sample_type VARCHAR DEFAULT 'phrase'")
        if "prompt_text" not in columns:
            statements.append("ALTER TABLE training_samples ADD COLUMN prompt_text VARCHAR")
        if "typed_text" not in columns:
            statements.append("ALTER TABLE training_samples ADD COLUMN typed_text VARCHAR")
        if "keystroke_count" not in columns:
            statements.append("ALTER TABLE training_samples ADD COLUMN keystroke_count INTEGER DEFAULT 0")

        if statements:
            with engine.begin() as connection:
                for statement in statements:
                    connection.execute(text(statement))

# Create tables
Base.metadata.create_all(bind=engine)
_ensure_sqlite_columns()
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
