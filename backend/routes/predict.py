"""
Prediction endpoint for KeyGuard
"""
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

try:
    from ..database.db import get_db
    from ..database.crud import get_active_session, get_behavior_profile, get_training_samples, get_user_by_username, log_intrusion
    from ..services.preprocessing import PreprocessingService
    from ..services.feature_pipeline import FeaturePipeline
    from ..services.detection import DetectionEngine
    from ..utils.logger import get_logger
except ImportError:
    from database.db import get_db
    from database.crud import get_user_by_username, get_active_session, log_intrusion, get_behavior_profile, get_training_samples
    from services.preprocessing import PreprocessingService
    from services.feature_pipeline import FeaturePipeline
    from services.detection import DetectionEngine
    from utils.logger import get_logger

router = APIRouter()
logger = get_logger()

PREDICTION_LABELS = {
    "normal": "NORMAL",
    "suspicious": "SUSPICIOUS",
    "intrusion": "INTRUDER",
}

class PredictRequest(BaseModel):
    """Request model for prediction endpoint"""
    username: str
    keystrokes: List[Dict[str, Any]]
    testCase: Optional[str] = None
    session_token: Optional[str] = None

def format_prediction_label(decision: str) -> str:
    """Convert internal decision labels to UI-facing API labels."""
    return PREDICTION_LABELS.get(decision.lower(), decision.upper())

@router.post("/predict")
async def predict_intrusion(
    request: PredictRequest,
    db: Session = Depends(get_db)
):
    """
    Predict intrusion based on keystroke data
    
    Request body:
    {
        "username": "user1",
        "keystrokes": [
            {"key": "a", "timestamp": 1000, "type": "keydown"},
            ...
        ],
        "testCase": "legitimate"
    }
    """
    try:
        username = request.username
        keystrokes = request.keystrokes
        test_case = request.testCase
        
        logger.info(f"Prediction request from {username} with {len(keystrokes)} keystrokes (test: {test_case})")
        
        # Validate user exists
        user = get_user_by_username(db, username)
        if not user:
            logger.warning(f"User not found: {username}")
            raise HTTPException(status_code=404, detail="User not found")

        if request.session_token:
            active_session = get_active_session(db, user.id)
            if not active_session or active_session.session_token != request.session_token:
                raise HTTPException(status_code=401, detail="Invalid or expired session")
        
        # Preprocess keystrokes
        valid_keystrokes, invalid_reasons = PreprocessingService.validate_keystroke_batch(keystrokes)
        if invalid_reasons:
            logger.warning(f"Invalid keystrokes: {invalid_reasons}")
        
        # Clean keystrokes
        cleaned = [PreprocessingService.sanitize_keystroke_data(k) for k in valid_keystrokes]
        cleaned = PreprocessingService.handle_missing_values(cleaned)
        cleaned = PreprocessingService.filter_noise_keys(cleaned, keep_space=False)
        cleaned = PreprocessingService.remove_outliers(cleaned)
        
        if len(cleaned) == 0:
            logger.warning("No valid keystrokes after preprocessing")
            return {
                "prediction": "NORMAL",
                "confidence": 0.95,
                "message": "No valid keystrokes to analyze"
            }
        
        # Extract features in both formats:
        # 1. Aggregated features for behavioral analysis
        _, feature_dict = FeaturePipeline.extract_features(cleaned)
        
        # 2. Individual dwell/flight times for ML model
        ml_features = FeaturePipeline.extract_features_for_ml_model(cleaned)
        
        logger.debug(f"Aggregated features: {feature_dict}")
        logger.debug(f"ML model features (count={len(ml_features)}): {ml_features}")

        user_profile = get_behavior_profile(db, user.id)
        profile_decision_internal, profile_details = DetectionEngine.evaluate_user_profile(
            feature_dict,
            user_profile,
        )
        profile_available = profile_details.get("available", False)
        profile_decision = format_prediction_label(profile_decision_internal)
        profile_confidence = float(profile_details.get("confidence", 0.0))
        
        training_vectors = get_training_samples(db, user.id)
        user_model_decision, user_model_details = DetectionEngine.evaluate_user_model(training_vectors, ml_features)

        model_decision = user_model_decision if user_model_details.get("available") else profile_decision_internal
        model_confidence = float(user_model_details.get("confidence", profile_confidence))

        prediction, confidence = DetectionEngine.combine_profile_and_model_decisions(
            profile_decision=profile_decision_internal,
            profile_confidence=profile_confidence,
            model_decision=model_decision.lower(),
            model_confidence=model_confidence,
            profile_available=profile_available,
        )
        prediction = format_prediction_label(prediction)

        if prediction == "INTRUDER" and request.session_token:
            active_session = get_active_session(db, user.id)
            if active_session:
                log_intrusion(
                    db=db,
                    user_id=user.id,
                    session_id=active_session.id,
                    detection_type="keystroke_anomaly",
                    rf_probability=0.0,
                    svm_anomaly_score=float(user_model_details.get("score", 0.0)),
                    decision=prediction.lower(),
                    keystroke_data={
                        "feature_dict": feature_dict,
                        "profile_details": profile_details,
                        "user_model_details": user_model_details,
                    },
                )

        logger.info(f"Prediction result for {username}: {prediction} ({confidence:.2f})")

        return {
            "prediction": prediction,
            "confidence": confidence,
            "features": feature_dict,
            "keystroke_count": len(cleaned),
            "details": {
                "model_decision": format_prediction_label(model_decision),
                "model_confidence": float(model_confidence),
                "profile_decision": profile_decision,
                "profile_confidence": profile_confidence,
                "profile_details": profile_details,
                "user_model_decision": format_prediction_label(user_model_decision),
                "user_model_details": user_model_details,
                "ml_feature_summary": FeaturePipeline.summarize_timing_vector(ml_features),
            },
            "message": f"User typing detected as {prediction}"
        }
    
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
            "user_specific_one_class_svm": True
        },
        "preferred_detector": "user-specific one-class svm"
    }
