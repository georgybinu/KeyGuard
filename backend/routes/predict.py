"""
Prediction endpoint for KeyGuard
"""
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from database.db import get_db
from database.crud import get_user_by_username, get_active_session, log_intrusion
from services.preprocessing import PreprocessingService
from services.feature_pipeline import FeaturePipeline
from services.detection import DetectionEngine
from models.model_loader import ModelLoader
from utils.config import MODEL_PATHS
from utils.helpers import format_response
from utils.logger import get_logger
import json

router = APIRouter()
logger = get_logger()

# Load models at startup
rf_model = ModelLoader.load_model(MODEL_PATHS["random_forest"], "random_forest")
svm_model = ModelLoader.load_model(MODEL_PATHS["one_class_svm"], "one_class_svm")
scaler = ModelLoader.load_scaler(MODEL_PATHS["scaler"])

class PredictRequest:
    """Request model for prediction endpoint"""
    def __init__(self, username: str, session_token: str, keystrokes: List[Dict[str, Any]]):
        self.username = username
        self.session_token = session_token
        self.keystrokes = keystrokes

@router.post("/predict")
async def predict_intrusion(
    username: str,
    session_token: str,
    keystrokes: List[Dict[str, Any]],
    db: Session = Depends(get_db)
):
    """
    Predict intrusion based on keystroke data
    
    Request body:
    {
        "username": "user1",
        "session_token": "token123",
        "keystrokes": [
            {"key_press_time": 1000, "key_release_time": 1050, "key": "a"},
            ...
        ]
    }
    """
    try:
        logger.info(f"Prediction request from {username} with {len(keystrokes)} keystrokes")
        
        # Validate user and session
        user = get_user_by_username(db, username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")
        
        session = get_active_session(db, user.id)
        if not session or session.session_token != session_token:
            logger.warning(f"Invalid or inactive session for user {username}")
            raise HTTPException(status_code=401, detail="Invalid session")
        
        # Preprocess keystrokes
        valid_keystrokes, invalid_reasons = PreprocessingService.validate_keystroke_batch(keystrokes)
        if invalid_reasons:
            logger.warning(f"Invalid keystrokes: {invalid_reasons}")
        
        # Clean keystrokes
        cleaned = [PreprocessingService.sanitize_keystroke_data(k) for k in valid_keystrokes]
        cleaned = PreprocessingService.handle_missing_values(cleaned)
        cleaned = PreprocessingService.remove_outliers(cleaned)
        
        if len(cleaned) == 0:
            logger.warning("No valid keystrokes after preprocessing")
            return format_response("normal", 0.9, 0.5, {"warning": "No valid keystrokes"})
        
        # Extract features in both formats:
        # 1. Aggregated features for behavioral analysis
        feature_vector, feature_dict = FeaturePipeline.extract_features(cleaned)
        
        # 2. Individual dwell/flight times for ML model (format: [d1, d2, ..., dN, f1, f2, ..., fN-1])
        ml_features = FeaturePipeline.extract_features_for_ml_model(cleaned)
        
        logger.debug(f"Aggregated features: {feature_dict}")
        logger.debug(f"ML model features (count={len(ml_features)}): {ml_features}")
        
        # Get predictions from models using ML format features
        rf_prob, rf_proba = ModelLoader.predict_random_forest(rf_model, ml_features)
        svm_score = ModelLoader.predict_one_class_svm(svm_model, ml_features)
        
        # Apply decision logic
        decision, confidence = DetectionEngine.apply_decision_logic(rf_prob, svm_score)
        
        # Log if suspicious or intrusion
        if decision in ["suspicious", "intrusion"]:
            log_intrusion(
                db, user.id, session.id,
                detection_type="model_ensemble",
                rf_probability=rf_prob,
                svm_anomaly_score=svm_score,
                decision=decision,
                keystroke_data={"num_keystrokes": len(cleaned), "features": feature_dict}
            )
            logger.warning(f"Logged {decision} event for user {username}")
        
        # Prepare response
        response = {
            "decision": decision,
            "confidence": {
                "rf_probability": float(rf_prob),
                "svm_anomaly_score": float(svm_score),
                "overall_confidence": DetectionEngine.compute_confidence_score(decision, rf_prob, svm_score)
            },
            "details": {
                "keystrokes_processed": len(cleaned),
                "features": feature_dict,
                "decision_factors": confidence.get('decision_factors', []),
                "ml_model_input": {
                    "dwell_count": len(cleaned),
                    "flight_count": len(cleaned) - 1,
                    "total_features": len(ml_features),
                    "feature_format": "[dwell1, dwell2, ..., dwellN, flight1, flight2, ..., flightN-1]"
                }
            }
        }
        
        logger.info(f"Prediction result for {username}: {decision}")
        return response
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@router.get("/predict/health")
async def predict_health_check():
    """Health check for prediction endpoint"""
    return {
        "status": "healthy",
        "service": "predict",
        "models_loaded": {
            "random_forest": rf_model is not None,
            "one_class_svm": svm_model is not None,
            "scaler": scaler is not None
        }
    }
