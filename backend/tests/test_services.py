"""
Unit tests for KeyGuard backend services and utilities
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.helpers import validate_keystroke_data, normalize_features, format_response
from services.feature_pipeline import FeaturePipeline
from services.preprocessing import PreprocessingService
from services.detection import DetectionEngine
from models.model_loader import ModelLoader, ModelLoadError

class TestValidation:
    """Tests for data validation"""
    
    def test_valid_keystroke_data(self):
        """Test valid keystroke data validation"""
        valid_data = {
            'key': 'a',
            'key_press_time': 1000,
            'key_release_time': 1050
        }
        assert validate_keystroke_data(valid_data) == True
    
    def test_invalid_keystroke_missing_field(self):
        """Test invalid keystroke with missing field"""
        invalid_data = {
            'key': 'a',
            'key_press_time': 1000
            # Missing key_release_time
        }
        assert validate_keystroke_data(invalid_data) == False
    
    def test_invalid_keystroke_bad_timestamp(self):
        """Test invalid keystroke with invalid timestamps"""
        invalid_data = {
            'key': 'a',
            'key_press_time': 1050,
            'key_release_time': 1000  # Release before press
        }
        assert validate_keystroke_data(invalid_data) == False
    
    def test_invalid_keystroke_non_numeric(self):
        """Test invalid keystroke with non-numeric timestamps"""
        invalid_data = {
            'key': 'a',
            'key_press_time': 'invalid',
            'key_release_time': 1050
        }
        assert validate_keystroke_data(invalid_data) == False

class TestFeatureExtraction:
    """Tests for feature extraction pipeline"""
    
    def test_dwell_time_computation(self):
        """Test dwell time calculation"""
        keystroke = {
            'key_press_time': 1000,
            'key_release_time': 1050
        }
        dwell = FeaturePipeline.compute_dwell_time(keystroke)
        assert dwell == 50
    
    def test_flight_time_computation(self):
        """Test flight time calculation"""
        prev_keystroke = {
            'key_press_time': 1000,
            'key_release_time': 1050
        }
        curr_keystroke = {
            'key_press_time': 1150,
            'key_release_time': 1200
        }
        flight = FeaturePipeline.compute_flight_time(prev_keystroke, curr_keystroke)
        assert flight == 100  # 1150 - 1050 = 100
    
    def test_flight_time_none_prev(self):
        """Test flight time with no previous keystroke"""
        curr_keystroke = {
            'key_press_time': 1150,
            'key_release_time': 1200
        }
        flight = FeaturePipeline.compute_flight_time(None, curr_keystroke)
        assert flight == 0
    
    def test_key_press_rate(self):
        """Test typing speed (key press rate)"""
        keystrokes = [
            {'key_press_time': 0, 'key_release_time': 50},
            {'key_press_time': 150, 'key_release_time': 200},
            {'key_press_time': 300, 'key_release_time': 350}
        ]
        rate = FeaturePipeline.compute_key_press_rate(keystrokes)
        # 2 intervals / 0.35 seconds = ~5.7 keys/sec
        assert rate > 5 and rate < 6
    
    def test_feature_extraction(self):
        """Test complete feature extraction"""
        keystrokes = [
            {'key_press_time': 0, 'key_release_time': 50, 'key': 'a'},
            {'key_press_time': 150, 'key_release_time': 200, 'key': 'b'},
            {'key_press_time': 300, 'key_release_time': 350, 'key': 'c'}
        ]
        features, feature_dict = FeaturePipeline.extract_features(keystrokes)
        
        assert len(features) == 5  # 5 features
        assert 'dwell_time' in feature_dict
        assert 'flight_time' in feature_dict
        assert 'key_press_rate' in feature_dict
        assert all(isinstance(f, float) for f in features)

class TestPreprocessing:
    """Tests for data preprocessing"""
    
    def test_keystroke_validation_batch(self):
        """Test batch keystroke validation"""
        batch = [
            {'key': 'a', 'key_press_time': 1000, 'key_release_time': 1050},
            {'key': 'b', 'key_press_time': 1150, 'key_release_time': 1000}  # Invalid
        ]
        valid, invalid = PreprocessingService.validate_keystroke_batch(batch)
        assert len(valid) == 1
        assert len(invalid) == 1
    
    def test_keystroke_sanitization(self):
        """Test keystroke data sanitization"""
        raw = {
            'key': '  A  ',
            'key_press_time': '1000',
            'key_release_time': 1050,
            'user_id': '123',
            'extra_field': 'ignored'
        }
        cleaned = PreprocessingService.sanitize_keystroke_data(raw)
        
        assert cleaned['key'] == 'A'
        assert isinstance(cleaned['key_press_time'], float)
        assert cleaned['user_id'] == 123
    
    def test_remove_outliers(self):
        """Test outlier removal"""
        batch = [
            {'key': 'a', 'key_press_time': 1000, 'key_release_time': 1050},  # Normal: 50ms
            {'key': 'b', 'key_press_time': 2000, 'key_release_time': 2010},  # Normal: 10ms
            {'key': 'c', 'key_press_time': 3000, 'key_release_time': 4500}   # Outlier: 1500ms
        ]
        filtered = PreprocessingService.remove_outliers(batch)
        assert len(filtered) == 2  # Outlier removed

class TestDetection:
    """Tests for detection engine"""
    
    def test_normal_behavior_decision(self):
        """Test detection of normal behavior"""
        decision, confidence = DetectionEngine.apply_decision_logic(0.95, 0.8)
        assert decision == "normal"
    
    def test_suspicious_behavior_decision(self):
        """Test detection of suspicious behavior"""
        # When RF says suspicious but SVM says normal, decision is suspicious
        decision, confidence = DetectionEngine.apply_decision_logic(0.45, 0.5)
        assert decision == "suspicious"
    
    def test_intrusion_behavior_decision(self):
        """Test detection of intrusion"""
        decision, confidence = DetectionEngine.apply_decision_logic(0.2, -0.8)
        assert decision == "intrusion"
    
    def test_decision_validation(self):
        """Test decision validation"""
        assert DetectionEngine.validate_decision("normal") == True
        assert DetectionEngine.validate_decision("suspicious") == True
        assert DetectionEngine.validate_decision("intrusion") == True
        assert DetectionEngine.validate_decision("unknown") == False
    
    def test_confidence_score_computation(self):
        """Test confidence score calculation"""
        score = DetectionEngine.compute_confidence_score("normal", 0.9, 0.7)
        assert 0 <= score <= 1

    def test_user_profile_normal_behavior(self):
        """Trained-user profile should accept close behavior."""
        decision, details = DetectionEngine.evaluate_user_profile(
            {
                "dwell_time": 52.0,
                "flight_time": 102.0,
            },
            {
                "dwell_time": {"mean": 50.0, "std_dev": 5.0, "sample_count": 5},
                "flight_time": {"mean": 100.0, "std_dev": 8.0, "sample_count": 5},
            }
        )
        assert decision == "normal"
        assert details["available"] is True

    def test_user_profile_intrusion_behavior(self):
        """Trained-user profile should flag large deviations."""
        decision, details = DetectionEngine.evaluate_user_profile(
            {
                "dwell_time": 180.0,
                "flight_time": 420.0,
            },
            {
                "dwell_time": {"mean": 50.0, "std_dev": 5.0, "sample_count": 5},
                "flight_time": {"mean": 100.0, "std_dev": 8.0, "sample_count": 5},
            }
        )
        assert decision == "intrusion"
        assert details["available"] is True

class TestModelLoader:
    """Tests for model loading"""
    
    def test_missing_model_raises(self):
        """Missing model files should fail loudly."""
        with pytest.raises(ModelLoadError):
            ModelLoader.load_model("/tmp/does-not-exist.pkl", "missing")
    
    def test_missing_scaler_raises(self):
        """Missing scaler files should fail loudly."""
        with pytest.raises(ModelLoadError):
            ModelLoader.load_scaler("/tmp/does-not-exist.pkl")

class TestFormatResponse:
    """Tests for response formatting"""
    
    def test_format_response(self):
        """Test response formatting"""
        response = format_response("normal", 0.95, 0.7, {"info": "test"})
        
        assert response['decision'] == "normal"
        assert response['confidence']['rf_probability'] == 0.95
        assert response['confidence']['svm_anomaly_score'] == 0.7
        assert response['details']['info'] == "test"

# Integration tests
class TestIntegration:
    """Integration tests for complete workflow"""
    
    def test_end_to_end_prediction(self):
        """Test complete prediction pipeline"""
        keystrokes = [
            {'key_press_time': 0, 'key_release_time': 50, 'key': 'h'},
            {'key_press_time': 150, 'key_release_time': 200, 'key': 'e'},
            {'key_press_time': 300, 'key_release_time': 350, 'key': 'l'},
            {'key_press_time': 450, 'key_release_time': 500, 'key': 'l'},
            {'key_press_time': 600, 'key_release_time': 650, 'key': 'o'},
        ]
        
        # Validate
        valid, invalid = PreprocessingService.validate_keystroke_batch(keystrokes)
        assert len(valid) > 0
        
        # Preprocess
        cleaned = [PreprocessingService.sanitize_keystroke_data(k) for k in valid]
        
        # Extract features
        features, feature_dict = FeaturePipeline.extract_features(cleaned)
        assert len(features) == 5
        
        summary = FeaturePipeline.summarize_timing_vector(features)
        assert len(summary) == 10

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
