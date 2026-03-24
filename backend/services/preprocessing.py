"""
Data preprocessing service for KeyGuard
"""
from typing import Dict, List, Any, Tuple
from utils.helpers import validate_keystroke_data
from utils.logger import get_logger
import numpy as np

logger = get_logger()

class PreprocessingService:
    """Handles data validation and cleaning"""
    
    @staticmethod
    def validate_keystroke_batch(keystroke_batch: List[Dict[str, Any]]) -> Tuple[List[Dict], List[str]]:
        """
        Validate batch of keystroke data
        
        Args:
            keystroke_batch: List of keystroke records
        
        Returns:
            Tuple of (valid_keystrokes, invalid_reasons)
        """
        valid_keystrokes = []
        invalid_reasons = []
        
        for i, keystroke in enumerate(keystroke_batch):
            if not validate_keystroke_data(keystroke):
                invalid_reasons.append(f"Keystroke {i}: Invalid format or timestamps")
                logger.warning(f"Invalid keystroke at index {i}: {keystroke}")
            else:
                valid_keystrokes.append(keystroke)
        
        return valid_keystrokes, invalid_reasons
    
    @staticmethod
    def sanitize_keystroke_data(keystroke: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize and clean keystroke data
        
        Args:
            keystroke: Raw keystroke record
        
        Returns:
            Cleaned keystroke record
        """
        cleaned = {
            'key': str(keystroke.get('key', '')).strip(),
            'key_press_time': float(keystroke.get('key_press_time', 0)),
            'key_release_time': float(keystroke.get('key_release_time', 0)),
            'user_id': int(keystroke.get('user_id', 0)) if keystroke.get('user_id') else None,
        }
        
        return cleaned
    
    @staticmethod
    def handle_missing_values(keystroke_batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Handle missing or null values in keystroke data
        
        Args:
            keystroke_batch: List of keystroke records
        
        Returns:
            Processed keystroke batch
        """
        processed = []
        
        for keystroke in keystroke_batch:
            # Skip if critical fields missing
            if keystroke.get('key_press_time') is None or keystroke.get('key_release_time') is None:
                logger.warning(f"Skipping keystroke with missing timestamps: {keystroke}")
                continue
            
            processed.append(keystroke)
        
        return processed
    
    @staticmethod
    def remove_outliers(keystroke_batch: List[Dict[str, Any]], 
                       thresholds: Dict[str, Tuple[float, float]] = None) -> List[Dict[str, Any]]:
        """
        Remove outlier keystrokes based on dwell/flight time
        
        Args:
            keystroke_batch: List of keystroke records
            thresholds: Dict with min/max for dwell_time and flight_time
        
        Returns:
            Filtered keystroke batch
        """
        if thresholds is None:
            thresholds = {
                'dwell_time': (5, 1000),      # 5ms to 1s
                'flight_time': (10, 1000),    # 10ms to 1s
            }
        
        filtered = []
        
        for keystroke in keystroke_batch:
            dwell_time = keystroke.get('key_release_time', 0) - keystroke.get('key_press_time', 0)
            
            # Check dwell time threshold
            if dwell_time < thresholds['dwell_time'][0] or dwell_time > thresholds['dwell_time'][1]:
                logger.debug(f"Removing keystroke with anomalous dwell time: {dwell_time}ms")
                continue
            
            filtered.append(keystroke)
        
        return filtered
