"""
Helper functions for KeyGuard backend
"""
from typing import Dict, List, Any
import numpy as np

def validate_keystroke_data(data: Dict[str, Any]) -> bool:
    """
    Validate keystroke data format
    
    Args:
        data: Dictionary with keys like 'key_press_time', 'key_release_time', 'key'
    
    Returns:
        True if valid, False otherwise
    """
    required_fields = ['key_press_time', 'key_release_time', 'key']
    
    for field in required_fields:
        if field not in data:
            return False
    
    # Validate timestamps
    if not isinstance(data['key_press_time'], (int, float)):
        return False
    if not isinstance(data['key_release_time'], (int, float)):
        return False
    
    # Release time should be after press time
    if data['key_release_time'] <= data['key_press_time']:
        return False
    
    return True

def normalize_features(features: List[float], scaler: Any = None) -> List[float]:
    """
    Normalize features to 0-1 range
    
    Args:
        features: List of feature values
        scaler: Optional sklearn scaler object
    
    Returns:
        Normalized features
    """
    if scaler is not None:
        return scaler.transform([features])[0].tolist()
    
    # Simple min-max normalization if no scaler provided
    features_array = np.array(features)
    min_val = features_array.min()
    max_val = features_array.max()
    
    if max_val - min_val == 0:
        return features
    
    normalized = (features_array - min_val) / (max_val - min_val)
    return normalized.tolist()

def format_response(decision: str, probability: float, anomaly_score: float, 
                   details: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Format response in standardized JSON format
    
    Args:
        decision: Classification decision (normal, suspicious, intrusion)
        probability: RF probability score
        anomaly_score: SVM anomaly score
        details: Additional details
    
    Returns:
        Formatted response dictionary
    """
    return {
        "decision": decision,
        "confidence": {
            "rf_probability": float(probability),
            "svm_anomaly_score": float(anomaly_score),
        },
        "details": details or {},
        "timestamp": None,
    }
