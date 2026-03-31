"""
Model loading and management for KeyGuard
"""
from typing import Any, Tuple
import pickle
import os
import numpy as np
import joblib

try:
    from ..utils.logger import get_logger
except ImportError:
    from utils.logger import get_logger

logger = get_logger()

class ModelLoadError(RuntimeError):
    """Raised when a required model or scaler cannot be loaded."""

class ModelLoader:
    """Handles loading and caching of ML models"""
    
    _models_cache = {}
    _scaler_cache = None
    
    @staticmethod
    def load_model(model_path: str, model_name: str = "model") -> Any:
        """
        Load pickle model from file
        
        Args:
            model_path: Path to model pickle file
            model_name: Name for logging
        
        Returns:
            Loaded model object
        """
        # Check cache first
        if model_name in ModelLoader._models_cache:
            logger.debug(f"Using cached model: {model_name}")
            return ModelLoader._models_cache[model_name]
        
        # Check if file exists
        if not os.path.exists(model_path):
            raise ModelLoadError(f"Model file not found: {model_path}")
        
        try:
            model = joblib.load(model_path)
            logger.info(f"Loaded model from {model_path}")
            ModelLoader._models_cache[model_name] = model
            return model
        except Exception as e:
            logger.warning(f"Joblib load failed for {model_path}: {str(e)}. Falling back to pickle.")
            try:
                with open(model_path, 'rb') as f:
                    model = pickle.load(f)
                logger.info(f"Loaded model from {model_path} using pickle fallback")
                ModelLoader._models_cache[model_name] = model
                return model
            except Exception as pickle_error:
                logger.error(f"Error loading model {model_path}: {str(pickle_error)}")
                raise ModelLoadError(f"Unable to load model from {model_path}") from pickle_error
    
    @staticmethod
    def load_scaler(scaler_path: str) -> Any:
        """
        Load feature scaler from file
        
        Args:
            scaler_path: Path to scaler pickle file
        
        Returns:
            Loaded scaler object
        """
        # Check cache
        if ModelLoader._scaler_cache is not None:
            logger.debug("Using cached scaler")
            return ModelLoader._scaler_cache
        
        if not os.path.exists(scaler_path):
            raise ModelLoadError(f"Scaler file not found: {scaler_path}")
        
        try:
            scaler = joblib.load(scaler_path)
            logger.info(f"Loaded scaler from {scaler_path}")
            ModelLoader._scaler_cache = scaler
            return scaler
        except Exception as e:
            logger.warning(f"Joblib load failed for {scaler_path}: {str(e)}. Falling back to pickle.")
            try:
                with open(scaler_path, 'rb') as f:
                    scaler = pickle.load(f)
                logger.info(f"Loaded scaler from {scaler_path} using pickle fallback")
                ModelLoader._scaler_cache = scaler
                return scaler
            except Exception as pickle_error:
                logger.error(f"Error loading scaler {scaler_path}: {str(pickle_error)}")
                raise ModelLoadError(f"Unable to load scaler from {scaler_path}") from pickle_error
    
    @staticmethod
    def predict_random_forest(rf_model: Any, features: list) -> Tuple[float, np.ndarray]:
        """
        Get prediction from Random Forest model
        
        Args:
            rf_model: Loaded RF model
            features: Feature vector
        
        Returns:
            Tuple of (probability, prediction_array)
        """
        try:
            # For 2D features
            features_array = np.array(features).reshape(1, -1)
            
            # Get probability prediction
            if hasattr(rf_model, 'predict_proba'):
                probabilities = rf_model.predict_proba(features_array)[0]
                # Assume class 1 is "normal" (0 = intrusion/anomaly)
                normal_prob = probabilities[1] if len(probabilities) > 1 else probabilities[0]
            else:
                # Fallback to predict
                prediction = rf_model.predict(features_array)[0]
                normal_prob = float(prediction)
            
            return float(normal_prob), np.array(probabilities) if hasattr(rf_model, 'predict_proba') else np.array([normal_prob])
        
        except Exception as e:
            logger.error(f"Error in RF prediction: {str(e)}")
            return 0.5, np.array([0.5, 0.5])
    
    @staticmethod
    def predict_one_class_svm(svm_model: Any, features: list) -> float:
        """
        Get prediction from One-Class SVM model
        
        Args:
            svm_model: Loaded SVM model
            features: Feature vector
        
        Returns:
            Anomaly score (positive = normal, negative = anomaly)
        """
        try:
            features_array = np.array(features).reshape(1, -1)
            
            # Get anomaly score (decision function)
            if hasattr(svm_model, 'decision_function'):
                score = svm_model.decision_function(features_array)[0]
            else:
                # Fallback to predict
                prediction = svm_model.predict(features_array)[0]
                score = float(prediction)
            
            return float(score)
        
        except Exception as e:
            logger.error(f"Error in SVM prediction: {str(e)}")
            return 0.0
