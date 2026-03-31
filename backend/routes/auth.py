"""
Authentication and session endpoints for KeyGuard.
"""
from datetime import datetime
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

try:
    from ..database.db import get_db
    from ..database.crud import (
        create_session,
        create_user,
        end_active_sessions,
        get_active_session,
        get_training_sample_count,
        get_user_by_email,
        get_user_by_session_token,
        get_user_by_username,
        update_user_credentials,
    )
    from ..utils.config import TOTAL_TRAINING_ROUNDS
    from ..utils.helpers import hash_password, verify_password
    from ..utils.logger import get_logger
except ImportError:
    from database.db import get_db
    from database.crud import (
        create_session,
        create_user,
        end_active_sessions,
        get_active_session,
        get_training_sample_count,
        get_user_by_email,
        get_user_by_session_token,
        get_user_by_username,
        update_user_credentials,
    )
    from utils.config import TOTAL_TRAINING_ROUNDS
    from utils.helpers import hash_password, verify_password
    from utils.logger import get_logger

router = APIRouter(prefix="/auth")
logger = get_logger()


class RegisterRequest(BaseModel):
    username: str
    email: str
    phone: Optional[str] = None
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class SessionResponse(BaseModel):
    username: str
    email: str
    phone: Optional[str]
    session_token: str
    training_completed: bool
    training_rounds: int
    created_at: str


def _build_auth_payload(user, session_token: str) -> dict:
    return {
        "username": user.username,
        "email": user.email,
        "phone": user.phone,
        "session_token": session_token,
        "training_completed": bool(user.training_completed),
        "training_rounds": int(user.training_rounds or 0),
        "created_at": user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
    }


@router.post("/register", response_model=SessionResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    username = request.username.strip()
    email = request.email.strip().lower()
    phone = request.phone.strip() if request.phone else None

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters")
    if len(request.password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")

    existing_user = get_user_by_username(db, username)
    if existing_user:
        raise HTTPException(status_code=409, detail="Username already exists")
    if get_user_by_email(db, email):
        raise HTTPException(status_code=409, detail="Email already exists")

    user = create_user(
        db,
        username=username,
        email=email,
        phone=phone,
        password_hash=hash_password(request.password),
    )
    session_token = str(uuid.uuid4())
    create_session(db, user.id, session_token)
    logger.info("Registered new user %s", username)
    return _build_auth_payload(user, session_token)


@router.post("/login", response_model=SessionResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    username = request.username.strip()
    user = get_user_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.password_hash:
        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    else:
        # Repair legacy accounts created before password support existed.
        update_user_credentials(db, user.id, phone=user.phone, password_hash=hash_password(request.password))
        user = get_user_by_username(db, username)

    end_active_sessions(db, user.id)
    session_token = str(uuid.uuid4())
    create_session(db, user.id, session_token)

    training_count = get_training_sample_count(db, user.id)
    if training_count != (user.training_rounds or 0):
        user.training_rounds = training_count
        user.training_completed = training_count >= TOTAL_TRAINING_ROUNDS
        db.commit()
        db.refresh(user)

    logger.info("User %s logged in", username)
    return _build_auth_payload(user, session_token)


@router.post("/logout")
async def logout(session_token: str, db: Session = Depends(get_db)):
    user = get_user_by_session_token(db, session_token)
    if not user:
        raise HTTPException(status_code=404, detail="Session not found")

    active_session = get_active_session(db, user.id)
    if active_session and active_session.session_token == session_token:
        end_active_sessions(db, user.id)
    return {"status": "success"}


@router.get("/session/{session_token}", response_model=SessionResponse)
async def get_session(session_token: str, db: Session = Depends(get_db)):
    user = get_user_by_session_token(db, session_token)
    if not user:
        raise HTTPException(status_code=404, detail="Session not found")
    return _build_auth_payload(user, session_token)
