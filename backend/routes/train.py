"""
Training endpoint for KeyGuard
"""
from fastapi import APIRouter, HTTPException, Body
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from database.db import get_db
from database.crud import get_user_by_username, update_behavior_profile
from services.preprocessing import PreprocessingService
from services.feature_pipeline import FeaturePipeline
from utils.logger import get_logger

router = APIRouter()
logger = get_logger()

class TrainingRequest(BaseModel):
    username: str
    keystrokes: List[Dict[str, Any]]
    round: Optional[int] = None

@router.post("/train")
async def train_user_profile(
    request: TrainingRequest,
    db: Session = Depends(get_db)
):
    """
    Train/update user behavior profile based on keystroke data
    
    Request body:
    {
        "username": "user1",
        "keystrokes": [
            {"key": "a", "timestamp": 1000, "type": "keydown"},
            ...
        ],
        "round": 1
    }
    """
    try:
        username = request.username
        keystrokes = request.keystrokes
        round_num = request.round
        
        logger.info(f"Training request for {username} with {len(keystrokes)} keystrokes (round {round_num})")
        
        # Get user
        user = get_user_by_username(db, username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")
        
        # Preprocess keystrokes
        valid_keystrokes, invalid_reasons = PreprocessingService.validate_keystroke_batch(keystrokes)
        if invalid_reasons:
            logger.warning(f"Invalid keystrokes during training: {invalid_reasons}")
        
        # Clean keystrokes
        cleaned = [PreprocessingService.sanitize_keystroke_data(k) for k in valid_keystrokes]
        cleaned = PreprocessingService.handle_missing_values(cleaned)
        cleaned = PreprocessingService.remove_outliers(cleaned)
        
        if len(cleaned) < 3:
            logger.warning(f"Insufficient keystrokes for training (need 3+, got {len(cleaned)})")
            # Don't fail - just log and continue, as single phrase rounds may have fewer keystrokes
        
        # Extract features in both formats:
        # 1. Aggregated features for behavioral profile
        feature_vector, feature_dict = FeaturePipeline.extract_features(cleaned)
        
        # 2. Individual dwell/flight times for ML model format
        ml_features = FeaturePipeline.extract_features_for_ml_model(cleaned)
        
        logger.info(f"Training with aggregated features: {feature_dict}")
        logger.info(f"Training with ML model features (count={len(ml_features)}): {ml_features}")
        
        # Update behavior profile with aggregated features
        import numpy as np
        for feature_name, feature_value in feature_dict.items():
            # In real scenario, would compute mean/std from multiple sessions
            std_dev = feature_value * 0.1  # 10% standard deviation
            
            update_behavior_profile(
                db, user.id, feature_name,
                mean_value=feature_value,
                std_dev=std_dev
            )
        
        logger.info(f"Updated behavior profile for user {username} (round {round_num})")
        
        return {
            "status": "success",
            "message": f"Round {round_num}: Profile updated with {len(cleaned)} keystrokes",
            "user_id": user.id,
            "username": username,
            "round": round_num,
            "keystrokes_processed": len(cleaned),
            "features_trained": list(feature_dict.keys()),
            "feature_values": feature_dict,
            "ml_model_features": {
                "dwell_count": len(cleaned),
                "flight_count": max(0, len(cleaned) - 1),
                "total_features": len(ml_features),
                "feature_vector": ml_features
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in training: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Training error: {str(e)}")

@router.get("/train/health")
async def train_health_check():
    """Health check for training endpoint"""
    return {
        "status": "healthy",
        "service": "train"
    }
