"""
Database models for KeyGuard
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from utils.config import DATABASE_URL

Base = declarative_base()

# SQLite database setup
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    """User profile model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
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

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
