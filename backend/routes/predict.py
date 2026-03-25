"""
Prediction endpoint for KeyGuard
"""
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
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
import numpy as np

router = APIRouter()
logger = get_logger()

# Load models at startup
rf_model = ModelLoader.load_model(MODEL_PATHS["random_forest"], "random_forest")
svm_model = ModelLoader.load_model(MODEL_PATHS["one_class_svm"], "one_class_svm")
scaler = ModelLoader.load_scaler(MODEL_PATHS["scaler"])

class PredictRequest(BaseModel):
    """Request model for prediction endpoint"""
    username: str
    keystrokes: List[Dict[str, Any]]
    testCase: Optional[str] = None
    session_token: Optional[str] = None

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
            return {
                "prediction": "NORMAL",
                "confidence": 0.95,
                "message": "No valid keystrokes to analyze"
            }
        
        # Extract features in both formats:
        # 1. Aggregated features for behavioral analysis
        feature_vector, feature_dict = FeaturePipeline.extract_features(cleaned)
        
        # 2. Individual dwell/flight times for ML model
        ml_features = FeaturePipeline.extract_features_for_ml_model(cleaned)
        
        logger.debug(f"Aggregated features: {feature_dict}")
        logger.debug(f"ML model features (count={len(ml_features)}): {ml_features}")
        
        # Use the trained models for prediction
        try:
            # Ensure features are numeric
            if isinstance(ml_features, list):
                ml_features = np.array(ml_features).reshape(1, -1)
            
            # Random Forest prediction
            if rf_model is not None:
                rf_prediction = rf_model.predict(ml_features)[0]
                rf_confidence = max(rf_model.predict_proba(ml_features)[0])
            else:
                rf_prediction = 1  # Default to normal
                rf_confidence = 0.5
            
            # One-Class SVM prediction (1 = normal, -1 = anomaly)
            if svm_model is not None and scaler is not None:
                ml_features_scaled = scaler.transform(ml_features)
                svm_prediction = svm_model.predict(ml_features_scaled)[0]
                svm_confidence = svm_model.decision_function(ml_features_scaled)[0]
            else:
                svm_prediction = 1  # Default to normal
                svm_confidence = 0.5
            
            logger.debug(f"RF Prediction: {rf_prediction}, Confidence: {rf_confidence}")
            logger.debug(f"SVM Prediction: {svm_prediction}, Decision Score: {svm_confidence}")
            
            # Decision logic:
            # If subject ID is 1 (trained user) in both models, it's normal
            # Otherwise, it's an intruder
            is_normal = (rf_prediction == 1) and (svm_prediction == 1)
            
            if is_normal:
                prediction = "NORMAL"
                # Use RF confidence as primary metric
                confidence = float(rf_confidence)
            else:
                prediction = "INTRUDER"
                # If SVM detected anomaly, use that as confidence
                if svm_prediction == -1:
                    confidence = min(0.99, abs(float(svm_confidence)))
                else:
                    confidence = 1.0 - float(rf_confidence)
            
            logger.info(f"Prediction result for {username}: {prediction} ({confidence:.2f})")
            
            return {
                "prediction": prediction,
                "confidence": confidence,
                "features": feature_dict,
                "keystroke_count": len(cleaned),
                "details": {
                    "rf_prediction": int(rf_prediction),
                    "rf_confidence": float(rf_confidence),
                    "svm_prediction": int(svm_prediction),
                    "svm_score": float(svm_confidence)
                },
                "message": f"User typing detected as {prediction}"
            }
        
        except Exception as e:
            logger.error(f"Error during ML prediction: {str(e)}", exc_info=True)
            # Fallback to conservative prediction
            return {
                "prediction": "NORMAL",
                "confidence": 0.5,
                "message": f"Error during prediction: {str(e)}"
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
            "random_forest": rf_model is not None,
            "one_class_svm": svm_model is not None,
            "scaler": scaler is not None
        }
    }
