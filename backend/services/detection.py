"""
Detection engine for intrusion classification
"""
from typing import Dict, Any, Tuple
from utils.config import NORMAL_THRESHOLD, SUSPICIOUS_THRESHOLD, DECISION_LABELS
from utils.logger import get_logger
import numpy as np

logger = get_logger()

class DetectionEngine:
    """Decision logic for intrusion detection"""
    
    @staticmethod
    def apply_decision_logic(rf_probability: float, svm_anomaly_score: float) -> Tuple[str, Dict[str, Any]]:
        """
        Apply decision logic combining RF and SVM results
        
        Args:
            rf_probability: Random Forest probability for normal class (0-1)
            svm_anomaly_score: One-Class SVM anomaly score (higher = more anomalous)
        
        Returns:
            Tuple of (decision, confidence_dict)
        """
        logger.debug(f"Decision logic - RF prob: {rf_probability}, SVM score: {svm_anomaly_score}")
        
        decision = DECISION_LABELS['normal']
        confidence = {
            'rf_probability': float(rf_probability),
            'svm_anomaly_score': float(svm_anomaly_score),
            'decision_factors': []
        }
        
        # Step 1: Check RF probability
        if rf_probability >= NORMAL_THRESHOLD:
            confidence['decision_factors'].append(f"RF: High confidence in normal (prob={rf_probability:.2f})")
        elif rf_probability >= SUSPICIOUS_THRESHOLD:
            confidence['decision_factors'].append(f"RF: Suspicious behavior (prob={rf_probability:.2f})")
            decision = DECISION_LABELS['suspicious']
        else:
            confidence['decision_factors'].append(f"RF: Low confidence in normal (prob={rf_probability:.2f})")
            decision = DECISION_LABELS['suspicious']
        
        # Step 2: Check SVM anomaly score
        if svm_anomaly_score > 0:
            # Positive score = normal
            confidence['decision_factors'].append("SVM: Normal behavior detected")
        else:
            # Negative score = anomalous
            confidence['decision_factors'].append(f"SVM: Anomaly detected (score={svm_anomaly_score:.2f})")
            
            # If both models suggest anomaly, classify as intrusion
            if decision == DECISION_LABELS['suspicious']:
                decision = DECISION_LABELS['intrusion']
        
        logger.info(f"Detection decision: {decision} - {confidence['decision_factors']}")
        
        return decision, confidence
    
    @staticmethod
    def validate_decision(decision: str) -> bool:
        """
        Validate decision is in allowed set
        
        Args:
            decision: Decision string
        
        Returns:
            True if valid, False otherwise
        """
        return decision in DECISION_LABELS.values()
    
    @staticmethod
    def compute_confidence_score(decision: str, rf_probability: float, 
                                svm_anomaly_score: float) -> float:
        """
        Compute overall confidence score (0-1)
        
        Args:
            decision: Classification decision
            rf_probability: RF probability
            svm_anomaly_score: SVM anomaly score
        
        Returns:
            Confidence score
        """
        if decision == DECISION_LABELS['normal']:
            # High confidence if both models agree
            confidence = (rf_probability + max(0, svm_anomaly_score)) / 2
        elif decision == DECISION_LABELS['intrusion']:
            # High confidence if both models flag anomaly
            confidence = (1 - rf_probability + abs(min(0, svm_anomaly_score))) / 2
        else:  # suspicious
            confidence = 0.5  # Medium confidence for ambiguous cases
        
        return float(np.clip(confidence, 0, 1))
