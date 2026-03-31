"""
Detection engine for intrusion classification
"""
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import OneClassSVM

try:
    from ..utils.config import NORMAL_THRESHOLD, SUSPICIOUS_THRESHOLD, DECISION_LABELS
    from ..utils.logger import get_logger
except ImportError:
    from utils.config import NORMAL_THRESHOLD, SUSPICIOUS_THRESHOLD, DECISION_LABELS
    from utils.logger import get_logger

logger = get_logger()

class DetectionEngine:
    """Decision logic for intrusion detection"""

    @staticmethod
    def evaluate_user_profile(current_features: Dict[str, float],
                              behavior_profile: Dict[str, Dict[str, float]]) -> Tuple[str, Dict[str, Any]]:
        """
        Compare current features against a user-specific baseline.
        """
        comparisons = {}
        z_scores = []

        for feature_name, feature_value in current_features.items():
            profile_stats = behavior_profile.get(feature_name)
            if not profile_stats or profile_stats.get("sample_count", 0) == 0:
                continue

            baseline_mean = float(profile_stats["mean"])
            baseline_std = float(profile_stats["std_dev"])
            sample_count = int(profile_stats.get("sample_count", 0))

            # Keep the profile usable even when training rounds are very consistent.
            tolerance = max(baseline_std, abs(baseline_mean) * 0.15, 10.0)
            z_score = abs(feature_value - baseline_mean) / tolerance

            comparisons[feature_name] = {
                "current": float(feature_value),
                "baseline_mean": baseline_mean,
                "baseline_std": baseline_std,
                "sample_count": sample_count,
                "z_score": float(z_score),
            }
            z_scores.append(z_score)

        if not z_scores:
            return DECISION_LABELS["normal"], {
                "available": False,
                "reason": "No user-specific training profile available",
                "confidence": 0.0,
                "comparisons": comparisons,
            }

        average_z = float(np.mean(z_scores))
        max_z = float(np.max(z_scores))
        min_samples = min(
            comparison["sample_count"] for comparison in comparisons.values()
        ) if comparisons else 0

        if min_samples < 3:
            decision = DECISION_LABELS["suspicious"]
        elif average_z <= 1.5 and max_z <= 3.0:
            decision = DECISION_LABELS["normal"]
        elif average_z <= 3.0 and max_z <= 5.0:
            decision = DECISION_LABELS["suspicious"]
        else:
            decision = DECISION_LABELS["intrusion"]

        confidence = float(np.clip(average_z / 4.0, 0.0, 0.99))
        if decision == DECISION_LABELS["normal"]:
            confidence = float(np.clip(1.0 - (average_z / 4.0), 0.5, 0.99))

        return decision, {
            "available": True,
            "average_z_score": average_z,
            "max_z_score": max_z,
            "minimum_samples": min_samples,
            "confidence": confidence,
            "comparisons": comparisons,
        }

    @staticmethod
    def combine_profile_and_model_decisions(profile_decision: str,
                                            profile_confidence: float,
                                            model_decision: str,
                                            model_confidence: float,
                                            profile_available: bool) -> Tuple[str, float]:
        """Blend user-specific and global-model decisions."""
        if not profile_available:
            return model_decision, model_confidence

        if profile_decision == DECISION_LABELS["intrusion"]:
            return DECISION_LABELS["intrusion"], max(profile_confidence, model_confidence)

        if profile_decision == DECISION_LABELS["suspicious"]:
            if model_decision == DECISION_LABELS["intrusion"]:
                return DECISION_LABELS["intrusion"], max(profile_confidence, model_confidence)
            return DECISION_LABELS["suspicious"], max(profile_confidence, 0.6)

        if model_decision == DECISION_LABELS["intrusion"] and model_confidence >= 0.9:
            return DECISION_LABELS["suspicious"], max(profile_confidence, model_confidence * 0.8)

        return DECISION_LABELS["normal"], max(profile_confidence, model_confidence)
    
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

    @staticmethod
    def evaluate_user_model(training_vectors: list[list[float]], current_vector: list[float]) -> Tuple[str, Dict[str, Any]]:
        """Fit a per-user One-Class SVM and score the current typing sample."""
        if len(training_vectors) < 5:
            return DECISION_LABELS["suspicious"], {
                "available": False,
                "reason": "At least 5 training rounds are required for user-specific OCSVM",
                "confidence": 0.0,
            }

        X_train = np.asarray(
            [DetectionEngine._summarize_vector(vector) for vector in training_vectors],
            dtype=float,
        )
        X_current = np.asarray(
            DetectionEngine._summarize_vector(current_vector),
            dtype=float,
        ).reshape(1, -1)

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_current_scaled = scaler.transform(X_current)

        model = OneClassSVM(
            kernel="rbf",
            gamma="scale",
            nu=min(0.12, max(0.05, 2.0 / len(training_vectors))),
        )
        model.fit(X_train_scaled)

        training_scores = model.decision_function(X_train_scaled)
        current_score = float(model.decision_function(X_current_scaled)[0])
        prediction = int(model.predict(X_current_scaled)[0])

        baseline_mean = float(np.mean(training_scores))
        baseline_std = float(np.std(training_scores)) or 1e-6
        suspicious_threshold = float(np.percentile(training_scores, 10) - (0.15 * baseline_std))
        intrusion_threshold = float(np.percentile(training_scores, 2) - (0.35 * baseline_std))
        normalized_margin = float(
            (current_score - intrusion_threshold) /
            max(suspicious_threshold - intrusion_threshold, 1e-6)
        )

        if prediction == 1 and current_score >= suspicious_threshold:
            decision = DECISION_LABELS["normal"]
            confidence = float(np.clip(0.65 + normalized_margin * 0.2, 0.55, 0.98))
        elif current_score >= intrusion_threshold:
            decision = DECISION_LABELS["suspicious"]
            confidence = float(np.clip(0.55 + (1.0 - normalized_margin) * 0.2, 0.55, 0.85))
        else:
            decision = DECISION_LABELS["intrusion"]
            confidence = float(
                np.clip(
                    0.75 + abs(current_score - intrusion_threshold) / max(abs(intrusion_threshold), 1.0),
                    0.75,
                    0.99,
                )
            )

        return decision, {
            "available": True,
            "prediction": prediction,
            "score": current_score,
            "training_score_mean": baseline_mean,
            "training_score_std": baseline_std,
            "suspicious_threshold": suspicious_threshold,
            "intrusion_threshold": intrusion_threshold,
            "confidence": confidence,
        }

    @staticmethod
    def _summarize_vector(vector: list[float]) -> list[float]:
        values = np.asarray(vector, dtype=float)
        if values.size == 0:
            return [0.0] * 10
        percentiles = np.percentile(values, [10, 25, 50, 75, 90])
        return [
            float(np.mean(values)),
            float(np.std(values)),
            float(np.min(values)),
            float(np.max(values)),
            float(percentiles[0]),
            float(percentiles[1]),
            float(percentiles[2]),
            float(percentiles[3]),
            float(percentiles[4]),
            float(np.mean(np.abs(np.diff(values)))) if values.size > 1 else 0.0,
        ]
