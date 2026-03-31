"""
Training endpoint for KeyGuard
"""
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

try:
    from ..database.db import get_db
    from ..database.crud import (
        clear_training_data,
        get_behavior_profile,
        get_training_sample_breakdown,
        get_training_sample_count,
        get_user_by_username,
        save_behavior_snapshot,
        save_training_sample,
        update_user_training_status,
    )
    from ..services.preprocessing import PreprocessingService
    from ..services.feature_pipeline import FeaturePipeline
    from ..utils.config import TOTAL_TRAINING_ROUNDS
    from ..utils.logger import get_logger
except ImportError:
    from database.db import get_db
    from database.crud import (
        clear_training_data,
        get_behavior_profile,
        get_training_sample_breakdown,
        get_training_sample_count,
        get_user_by_username,
        save_behavior_snapshot,
        save_training_sample,
        update_user_training_status,
    )
    from services.preprocessing import PreprocessingService
    from services.feature_pipeline import FeaturePipeline
    from utils.config import TOTAL_TRAINING_ROUNDS
    from utils.logger import get_logger

router = APIRouter()
logger = get_logger()

class TrainingRequest(BaseModel):
    username: str
    keystrokes: List[Dict[str, Any]]
    round: Optional[int] = None
    phrase: Optional[str] = None
    sample_type: Optional[str] = "phrase"
    prompt_text: Optional[str] = None
    typed_text: Optional[str] = None

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
        sample_type = (request.sample_type or "phrase").strip().lower()

        if sample_type not in {"phrase", "paragraph"}:
            raise HTTPException(status_code=400, detail="sample_type must be 'phrase' or 'paragraph'")
        
        logger.info(f"Training request for {username} with {len(keystrokes)} keystrokes (round {round_num})")
        
        # Get user
        user = get_user_by_username(db, username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")
        
        if round_num == 1:
            clear_training_data(db, user.id)

        # Preprocess keystrokes
        valid_keystrokes, invalid_reasons = PreprocessingService.validate_keystroke_batch(keystrokes)
        if invalid_reasons:
            logger.warning(f"Invalid keystrokes during training: {invalid_reasons}")
        
        # Clean keystrokes
        cleaned = [PreprocessingService.sanitize_keystroke_data(k) for k in valid_keystrokes]
        cleaned = PreprocessingService.handle_missing_values(cleaned)
        cleaned = PreprocessingService.filter_noise_keys(cleaned, keep_space=False)
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
        
        # Persist each training round so prediction can build a real per-user baseline.
        save_behavior_snapshot(db, user.id, feature_dict)
        save_training_sample(
            db,
            user.id,
            round_num or 1,
            ml_features,
            phrase=request.phrase,
            sample_type=sample_type,
            prompt_text=request.prompt_text or request.phrase,
            typed_text=request.typed_text,
            keystroke_count=len(cleaned),
        )
        behavior_profile = get_behavior_profile(db, user.id)
        trained_rounds = get_training_sample_count(db, user.id)
        training_breakdown = get_training_sample_breakdown(db, user.id)
        update_user_training_status(db, user.id, trained_rounds)
        
        logger.info(f"Updated behavior profile for user {username} (round {round_num}, trained_rounds={trained_rounds})")
        
        return {
            "status": "success",
            "message": f"Round {round_num}: Profile updated with {len(cleaned)} keystrokes",
            "user_id": user.id,
            "username": username,
            "round": round_num,
            "keystrokes_processed": len(cleaned),
            "features_trained": list(feature_dict.keys()),
            "feature_values": feature_dict,
            "profile_summary": {
                "trained_rounds": trained_rounds,
                "training_completed": trained_rounds >= TOTAL_TRAINING_ROUNDS,
                "required_rounds": TOTAL_TRAINING_ROUNDS,
                "sample_breakdown": training_breakdown,
                "features_available": list(behavior_profile.keys()),
            },
            "ml_model_features": {
                "dwell_count": len(cleaned),
                "flight_count": max(0, len(cleaned) - 1),
                "total_features": len(ml_features),
                "feature_vector": ml_features
            },
            "sample_type": sample_type,
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
