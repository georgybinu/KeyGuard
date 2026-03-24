"""
CRUD operations for KeyGuard database
"""
from sqlalchemy.orm import Session
from datetime import datetime
from database.db import User, Session as DBSession, IntrusionLog, BehaviorProfile
import json

# User CRUD
def create_user(db: Session, username: str, email: str) -> User:
    """Create new user"""
    db_user = User(username=username, email=email)
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
    
    return {p.feature_name: {"mean": p.mean_value, "std_dev": p.std_dev} for p in profiles}
