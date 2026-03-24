"""
Model loading and management for KeyGuard
"""
from typing import Dict, Any, Tuple
import pickle
import os
import numpy as np
from utils.logger import get_logger

logger = get_logger()

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
            logger.warning(f"Model file not found: {model_path}. Creating mock model.")
            # Return mock model for demo
            return ModelLoader._create_mock_model(model_name)
        
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            logger.info(f"Loaded model from {model_path}")
            ModelLoader._models_cache[model_name] = model
            return model
        except Exception as e:
            logger.error(f"Error loading model {model_path}: {str(e)}")
            return ModelLoader._create_mock_model(model_name)
    
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
            logger.warning(f"Scaler file not found: {scaler_path}. Creating mock scaler.")
            return ModelLoader._create_mock_scaler()
        
        try:
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            logger.info(f"Loaded scaler from {scaler_path}")
            ModelLoader._scaler_cache = scaler
            return scaler
        except Exception as e:
            logger.error(f"Error loading scaler {scaler_path}: {str(e)}")
            return ModelLoader._create_mock_scaler()
    
    @staticmethod
    def _create_mock_model(model_type: str) -> Any:
        """Create mock model for demo/testing"""
        class MockModel:
            def __init__(self, model_type):
                self.model_type = model_type
            
            def predict(self, X):
                """Mock predict returning dummy predictions"""
                if self.model_type == "random_forest":
                    # Return probabilities in [0, 1]
                    return np.random.uniform(0.4, 0.9, size=len(X) if isinstance(X, list) else 1)
                elif self.model_type == "one_class_svm":
                    # Return anomaly scores
                    return np.random.uniform(-1, 1, size=len(X) if isinstance(X, list) else 1)
                return np.array([0.5])
            
            def predict_proba(self, X):
                """Mock predict_proba for RF"""
                if self.model_type == "random_forest":
                    n_samples = len(X) if isinstance(X, list) else 1
                    probs = np.random.uniform(0.3, 0.95, size=(n_samples, 2))
                    # Normalize to sum to 1
                    return probs / probs.sum(axis=1, keepdims=True)
                return None
        
        return MockModel(model_type)
    
    @staticmethod
    def _create_mock_scaler() -> Any:
        """Create mock scaler for demo/testing"""
        class MockScaler:
            def transform(self, X):
                """Mock transform - simple normalization"""
                X = np.array(X)
                return (X - np.mean(X, axis=0)) / (np.std(X, axis=0) + 1e-8)
        
        return MockScaler()
    
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
