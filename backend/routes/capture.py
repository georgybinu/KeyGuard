"""
Capture endpoint for handling keystroke data ingestion
"""
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database.db import get_db
from database.crud import get_user_by_username, create_session, get_active_session
from utils.logger import get_logger
import uuid

router = APIRouter()
logger = get_logger()

@router.post("/capture/start")
async def start_capture_session(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Start a new capture session for keystroke monitoring
    
    Request body:
    {
        "username": "user1"
    }
    """
    try:
        logger.info(f"Starting capture session for {username}")
        
        # Get or create user
        user = get_user_by_username(db, username)
        if not user:
            # Create new user if doesn't exist
            from database.crud import create_user
            user = create_user(db, username, f"{username}@keyguard.local")
            logger.info(f"Created new user: {username}")
        
        # Check for existing active session
        existing_session = get_active_session(db, user.id)
        if existing_session:
            logger.info(f"Returning existing active session for {username}")
            return {
                "status": "active",
                "session_token": existing_session.session_token,
                "session_id": existing_session.id,
                "user_id": user.id,
                "message": "Using existing active session"
            }
        
        # Create new session
        session_token = str(uuid.uuid4())
        db_session = create_session(db, user.id, session_token)
        
        logger.info(f"Created new capture session {db_session.id} for {username}")
        
        return {
            "status": "success",
            "session_token": session_token,
            "session_id": db_session.id,
            "user_id": user.id,
            "message": "Capture session started"
        }
    
    except Exception as e:
        logger.error(f"Error starting capture session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Session start error: {str(e)}")

@router.post("/capture/end")
async def end_capture_session(
    username: str,
    session_token: str,
    db: Session = Depends(get_db)
):
    """
    End an active capture session
    
    Request body:
    {
        "username": "user1",
        "session_token": "token123"
    }
    """
    try:
        logger.info(f"Ending capture session for {username}")
        
        # Get user
        user = get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get active session
        session = get_active_session(db, user.id)
        if not session or session.session_token != session_token:
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # End session
        from database.crud import end_session
        end_session(db, session.id)
        
        logger.info(f"Ended capture session {session.id} for {username}")
        
        return {
            "status": "success",
            "message": "Capture session ended",
            "session_id": session.id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error ending capture session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Session end error: {str(e)}")

@router.get("/capture/status")
async def capture_status(
    username: str,
    db: Session = Depends(get_db)
):
    """
    Get current capture session status for user
    """
    try:
        # Get user
        user = get_user_by_username(db, username)
        if not user:
            return {"status": "inactive", "message": "User not found"}
        
        # Get active session
        session = get_active_session(db, user.id)
        
        if session:
            logger.debug(f"Session active for {username}")
            return {
                "status": "active",
                "session_id": session.id,
                "session_token": session.session_token,
                "start_time": session.start_time.isoformat() if session.start_time else None
            }
        else:
            logger.debug(f"No active session for {username}")
            return {
                "status": "inactive",
                "message": "No active session"
            }
    
    except Exception as e:
        logger.error(f"Error getting capture status: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Status check error: {str(e)}")

@router.post("/register")
async def register_user(
    username: str = None,
    email: str = None,
    phone: str = None,
    password: str = None,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    Query parameters:
    - username: Username for the account
    - email: Email address
    - phone: Phone number
    - password: Password (optional, for demo)
    """
    try:
        if not username or not email:
            raise HTTPException(status_code=400, detail="Username and email are required")
        
        logger.info(f"Registering new user: {username}")
        
        # Check if user already exists
        existing_user = get_user_by_username(db, username)
        if existing_user:
            raise HTTPException(status_code=409, detail="Username already exists")
        
        # Create new user
        from database.crud import create_user
        user = create_user(db, username, email)
        
        logger.info(f"Successfully registered user: {username}")
        
        return {
            "status": "success",
            "message": f"User {username} registered successfully",
            "username": username,
            "email": email,
            "phone": phone or "",
            "user_id": user.id,
            "token": str(uuid.uuid4())
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")

@router.get("/capture/health")
async def capture_health_check():
    """Health check for capture endpoint"""
    return {
        "status": "healthy",
        "service": "capture"
    }

