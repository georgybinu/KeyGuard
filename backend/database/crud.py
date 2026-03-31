"""
CRUD operations for KeyGuard database
"""
from sqlalchemy.orm import Session
from datetime import datetime
import json
import math

try:
    from .db import User, Session as DBSession, IntrusionLog, BehaviorProfile, TrainingSample
except ImportError:
    from database.db import User, Session as DBSession, IntrusionLog, BehaviorProfile, TrainingSample

# User CRUD
def create_user(db: Session, username: str, email: str, phone: str = None, password_hash: str = None) -> User:
    """Create new user"""
    db_user = User(username=username, email=email, phone=phone, password_hash=password_hash)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int) -> User:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_username(db: Session, username: str) -> User:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()

def get_user_by_session_token(db: Session, session_token: str) -> User:
    """Get user by active session token."""
    session = db.query(DBSession).filter(
        DBSession.session_token == session_token,
        DBSession.is_active == True
    ).first()
    if not session:
        return None
    return get_user(db, session.user_id)

def update_user_credentials(db: Session, user_id: int, phone: str = None, password_hash: str = None) -> User:
    """Update optional user credential fields."""
    user = get_user(db, user_id)
    if not user:
        return None
    if phone is not None:
        user.phone = phone
    if password_hash is not None:
        user.password_hash = password_hash
    db.commit()
    db.refresh(user)
    return user

def update_user_training_status(db: Session, user_id: int, training_rounds: int) -> User:
    """Persist training progress on the user record."""
    user = get_user(db, user_id)
    if not user:
        return None
    user.training_rounds = training_rounds
    user.training_completed = training_rounds >= 10
    db.commit()
    db.refresh(user)
    return user

# Session CRUD
def create_session(db: Session, user_id: int, session_token: str) -> DBSession:
    """Create new session"""
    db_session = DBSession(user_id=user_id, session_token=session_token)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session

def get_active_session(db: Session, user_id: int) -> DBSession:
    """Get active session for user"""
    return db.query(DBSession).filter(
        DBSession.user_id == user_id,
        DBSession.is_active == True
    ).first()

def end_active_sessions(db: Session, user_id: int) -> None:
    """End every active session for a user."""
    sessions = db.query(DBSession).filter(
        DBSession.user_id == user_id,
        DBSession.is_active == True
    ).all()
    for session in sessions:
        session.is_active = False
        session.end_time = datetime.utcnow()
    if sessions:
        db.commit()

def end_session(db: Session, session_id: int) -> DBSession:
    """End user session"""
    db_session = db.query(DBSession).filter(DBSession.id == session_id).first()
    if db_session:
        db_session.is_active = False
        db_session.end_time = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session

# Intrusion Log CRUD
def log_intrusion(db: Session, user_id: int, session_id: int, 
                 detection_type: str, rf_probability: float, 
                 svm_anomaly_score: float, decision: str, 
                 keystroke_data: dict) -> IntrusionLog:
    """Log intrusion event"""
    db_log = IntrusionLog(
        user_id=user_id,
        session_id=session_id,
        detection_type=detection_type,
        rf_probability=rf_probability,
        svm_anomaly_score=svm_anomaly_score,
        decision=decision,
        keystroke_data=json.dumps(keystroke_data)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

def get_intrusion_logs(db: Session, user_id: int, limit: int = 100) -> list:
    """Get intrusion logs for user"""
    return db.query(IntrusionLog).filter(
        IntrusionLog.user_id == user_id
    ).order_by(IntrusionLog.timestamp.desc()).limit(limit).all()

# Behavior Profile CRUD
def create_behavior_profile_entry(db: Session, user_id: int, feature_name: str,
                                 mean_value: float, std_dev: float = 0.0) -> BehaviorProfile:
    """Create a single behavior profile observation."""
    profile = BehaviorProfile(
        user_id=user_id,
        feature_name=feature_name,
        mean_value=mean_value,
        std_dev=std_dev
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return profile

def update_behavior_profile(db: Session, user_id: int, feature_name: str, 
                           mean_value: float, std_dev: float) -> BehaviorProfile:
    """Update user behavior profile"""
    profile = db.query(BehaviorProfile).filter(
        BehaviorProfile.user_id == user_id,
        BehaviorProfile.feature_name == feature_name
    ).first()
    
    if profile:
        profile.mean_value = mean_value
        profile.std_dev = std_dev
        profile.updated_at = datetime.utcnow()
    else:
        profile = BehaviorProfile(
            user_id=user_id,
            feature_name=feature_name,
            mean_value=mean_value,
            std_dev=std_dev
        )
        db.add(profile)
    
    db.commit()
    db.refresh(profile)
    return profile

def get_behavior_profile(db: Session, user_id: int) -> dict:
    """Get user behavior profile"""
    profiles = db.query(BehaviorProfile).filter(
        BehaviorProfile.user_id == user_id
    ).all()

    aggregated_profile = {}
    grouped_values = {}

    for profile in profiles:
        grouped_values.setdefault(profile.feature_name, []).append(float(profile.mean_value))

    for feature_name, values in grouped_values.items():
        if not values:
            continue
        mean_value = sum(values) / len(values)
        variance = sum((value - mean_value) ** 2 for value in values) / len(values)
        aggregated_profile[feature_name] = {
            "mean": mean_value,
            "std_dev": math.sqrt(variance),
            "sample_count": len(values),
        }

    return aggregated_profile

def save_behavior_snapshot(db: Session, user_id: int, feature_values: dict) -> None:
    """Persist a training snapshot so we can build a per-user baseline over time."""
    for feature_name, value in feature_values.items():
        create_behavior_profile_entry(
            db=db,
            user_id=user_id,
            feature_name=feature_name,
            mean_value=float(value),
            std_dev=0.0,
        )

def clear_training_data(db: Session, user_id: int) -> None:
    """Reset training samples and behavior snapshots for a user."""
    db.query(BehaviorProfile).filter(BehaviorProfile.user_id == user_id).delete()
    db.query(TrainingSample).filter(TrainingSample.user_id == user_id).delete()
    db.commit()

def save_training_sample(db: Session, user_id: int, round_number: int, feature_vector: list, phrase: str = None) -> TrainingSample:
    """Persist a fixed-length training vector for per-user anomaly detection."""
    sample = TrainingSample(
        user_id=user_id,
        round_number=round_number,
        phrase=phrase,
        feature_vector=json.dumps([float(value) for value in feature_vector]),
    )
    db.add(sample)
    db.commit()
    db.refresh(sample)
    return sample

def get_training_samples(db: Session, user_id: int) -> list:
    """Return deserialized training vectors for a user."""
    samples = db.query(TrainingSample).filter(
        TrainingSample.user_id == user_id
    ).order_by(TrainingSample.round_number.asc(), TrainingSample.id.asc()).all()
    return [json.loads(sample.feature_vector) for sample in samples]

def get_training_sample_count(db: Session, user_id: int) -> int:
    """Count saved training samples for a user."""
    return db.query(TrainingSample).filter(TrainingSample.user_id == user_id).count()
