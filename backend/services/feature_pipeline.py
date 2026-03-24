"""
Feature extraction and pipeline for KeyGuard
"""
from typing import Dict, List, Any, Tuple
import numpy as np
from utils.config import FEATURE_NAMES
from utils.logger import get_logger

logger = get_logger()

class FeaturePipeline:
    """Converts raw keystroke data into behavioral features"""
    
    @staticmethod
    def compute_dwell_time(keystroke: Dict[str, Any]) -> float:
        """
        Compute dwell time (key hold duration)
        
        Args:
            keystroke: Keystroke record with press and release times
        
        Returns:
            Dwell time in milliseconds
        """
        dwell = keystroke.get('key_release_time', 0) - keystroke.get('key_press_time', 0)
        return max(0, dwell)
    
    @staticmethod
    def compute_flight_time(prev_keystroke: Dict[str, Any], curr_keystroke: Dict[str, Any]) -> float:
        """
        Compute flight time (time between key release and next press)
        
        Args:
            prev_keystroke: Previous keystroke record
            curr_keystroke: Current keystroke record
        
        Returns:
            Flight time in milliseconds
        """
        if prev_keystroke is None:
            return 0
        
        flight = curr_keystroke.get('key_press_time', 0) - prev_keystroke.get('key_release_time', 0)
        return max(0, flight)
    
    @staticmethod
    def compute_key_press_rate(keystroke_batch: List[Dict[str, Any]]) -> float:
        """
        Compute typing speed (keystrokes per second)
        
        Args:
            keystroke_batch: List of keystroke records
        
        Returns:
            Key press rate (keys per second)
        """
        if len(keystroke_batch) < 2:
            return 0
        
        time_span = keystroke_batch[-1].get('key_release_time', 0) - keystroke_batch[0].get('key_press_time', 0)
        
        if time_span == 0:
            return 0
        
        return (len(keystroke_batch) - 1) / (time_span / 1000.0)  # Convert ms to seconds
    
    @staticmethod
    def compute_key_release_interval(keystroke_batch: List[Dict[str, Any]]) -> float:
        """
        Compute average time between consecutive key releases
        
        Args:
            keystroke_batch: List of keystroke records
        
        Returns:
            Average release interval in milliseconds
        """
        if len(keystroke_batch) < 2:
            return 0
        
        intervals = []
        for i in range(1, len(keystroke_batch)):
            interval = keystroke_batch[i].get('key_press_time', 0) - keystroke_batch[i-1].get('key_release_time', 0)
            intervals.append(interval)
        
        return np.mean(intervals) if intervals else 0
    
    @staticmethod
    def compute_typing_speed(keystroke_batch: List[Dict[str, Any]]) -> float:
        """
        Compute overall typing speed (average dwell + flight time)
        
        Args:
            keystroke_batch: List of keystroke records
        
        Returns:
            Average key interval (dwell + flight) in milliseconds
        """
        if len(keystroke_batch) == 0:
            return 0
        
        intervals = []
        for keystroke in keystroke_batch:
            dwell = FeaturePipeline.compute_dwell_time(keystroke)
            intervals.append(dwell)
        
        return np.mean(intervals) if intervals else 0
    
    @classmethod
    def extract_features(cls, keystroke_batch: List[Dict[str, Any]]) -> Tuple[List[float], Dict[str, float]]:
        """
        Extract behavioral features from keystroke batch
        
        Args:
            keystroke_batch: List of keystroke records
        
        Returns:
            Tuple of (feature_vector, feature_dict)
        """
        if len(keystroke_batch) == 0:
            logger.warning("Empty keystroke batch")
            return [0] * len(FEATURE_NAMES), {}
        
        feature_dict = {}
        
        # Compute individual features
        dwell_times = [cls.compute_dwell_time(k) for k in keystroke_batch]
        flight_times = [cls.compute_flight_time(keystroke_batch[i-1] if i > 0 else None, keystroke_batch[i]) 
                        for i in range(len(keystroke_batch))]
        
        feature_dict['dwell_time'] = float(np.mean(dwell_times)) if dwell_times else 0
        feature_dict['flight_time'] = float(np.mean(flight_times)) if flight_times else 0
        feature_dict['key_press_rate'] = cls.compute_key_press_rate(keystroke_batch)
        feature_dict['key_release_interval'] = cls.compute_key_release_interval(keystroke_batch)
        feature_dict['typing_speed'] = cls.compute_typing_speed(keystroke_batch)
        
        # Build feature vector in standard order
        feature_vector = [
            feature_dict.get(name, 0) for name in FEATURE_NAMES
        ]
        
        logger.debug(f"Extracted features: {feature_dict}")
        
        return feature_vector, feature_dict
    
    @classmethod
    def extract_features_for_ml_model(cls, keystroke_batch: List[Dict[str, Any]]) -> List[float]:
        """
        Extract features in ML model format: [dwell1, dwell2, ..., dwellN, flight1, flight2, ..., flightN-1]
        
        This is the format expected by the actual ML model (e.g., for "greyc laboratory" phrase)
        
        Args:
            keystroke_batch: List of keystroke records
        
        Returns:
            Feature list in ML model format
        """
        if len(keystroke_batch) == 0:
            logger.warning("Empty keystroke batch for ML model")
            return []
        
        # Extract individual dwell times for each keystroke
        dwell_times = [cls.compute_dwell_time(k) for k in keystroke_batch]
        
        # Extract individual flight times between keystrokes (N-1 values for N keystrokes)
        flight_times = [cls.compute_flight_time(keystroke_batch[i-1] if i > 0 else None, keystroke_batch[i]) 
                        for i in range(len(keystroke_batch))]
        
        # Remove the first flight time (before first keystroke) to get N-1 values
        flight_times = flight_times[1:]
        
        # Concatenate: [dwell1, dwell2, ..., dwellN, flight1, flight2, ..., flightN-1]
        feature_vector = dwell_times + flight_times
        
        logger.debug(f"ML Model Features - Dwells: {len(dwell_times)}, Flights: {len(flight_times)}, Total: {len(feature_vector)}")
        logger.debug(f"Feature vector: {feature_vector}")
        
        return feature_vector
