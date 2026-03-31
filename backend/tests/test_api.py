"""
Integration tests for KeyGuard API endpoints
Tests the FastAPI application with realistic scenarios
"""
import pytest
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

TEST_DB_FILE = os.path.join(tempfile.gettempdir(), "keyguard_test_api.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"

from fastapi.testclient import TestClient
from app import app
from database.db import Base, engine, SessionLocal
from database.crud import create_user, create_session
import uuid

# Setup test database
@pytest.fixture(autouse=True)
def setup_database():
    """Setup and teardown test database"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
def test_user():
    """Create test user"""
    db = SessionLocal()
    user = create_user(db, "testuser", "test@keyguard.local")
    db.close()
    return user

@pytest.fixture
def test_session(test_user):
    """Create test session"""
    db = SessionLocal()
    session = create_session(db, test_user.id, str(uuid.uuid4()))
    db.close()
    return session

class TestRootEndpoint:
    """Test root API endpoint"""
    
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["application"] == "KeyGuard Backend"
        assert "endpoints" in data

class TestHealthEndpoints:
    """Test health check endpoints"""
    
    def test_health_check(self, client):
        """Test system health check"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "KeyGuard Backend"
    
    def test_config_endpoint(self, client):
        """Test config endpoint"""
        response = client.get("/config")
        assert response.status_code == 200
        data = response.json()
        assert "thresholds" in data
        assert "features" in data
        assert data["features"]["expected_feature_count"] == 5
    
    def test_status_endpoint(self, client):
        """Test status endpoint"""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "running"
        assert "components" in data

class TestAuthEndpoints:
    """Test registration, login, and session restoration."""

    def test_register_login_and_restore_session(self, client):
        response = client.post(
            "/auth/register",
            json={
                "username": "alice",
                "email": "alice@example.com",
                "phone": "1234567890",
                "password": "secret123",
            }
        )
        assert response.status_code == 200
        register_data = response.json()
        assert register_data["training_completed"] is False
        assert register_data["training_rounds"] == 0

        login_response = client.post(
            "/auth/login",
            json={
                "username": "alice",
                "password": "secret123",
            }
        )
        assert login_response.status_code == 200
        login_data = login_response.json()
        assert login_data["session_token"]

        restore_response = client.get(f"/auth/session/{login_data['session_token']}")
        assert restore_response.status_code == 200
        restore_data = restore_response.json()
        assert restore_data["username"] == "alice"

    def test_login_rejects_bad_password(self, client):
        client.post(
            "/auth/register",
            json={
                "username": "bob",
                "email": "bob@example.com",
                "phone": "1234567890",
                "password": "right-password",
            }
        )
        response = client.post(
            "/auth/login",
            json={
                "username": "bob",
                "password": "wrong-password",
            }
        )
        assert response.status_code == 401

    def test_register_rejects_duplicate_email(self, client):
        client.post(
            "/auth/register",
            json={
                "username": "firstuser",
                "email": "shared@example.com",
                "phone": "1111111111",
                "password": "secret123",
            }
        )
        response = client.post(
            "/auth/register",
            json={
                "username": "seconduser",
                "email": "shared@example.com",
                "phone": "2222222222",
                "password": "secret123",
            }
        )
        assert response.status_code == 409

    def test_register_rejects_short_password(self, client):
        response = client.post(
            "/auth/register",
            json={
                "username": "tiny",
                "email": "tiny@example.com",
                "phone": "1234567890",
                "password": "short",
            }
        )
        assert response.status_code == 400

class TestCaptureEndpoints:
    """Test capture session endpoints"""
    
    def test_start_capture_session(self, client):
        """Test starting a capture session"""
        response = client.post(
            "/capture/start",
            params={"username": "newuser"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "session_token" in data
        assert "session_id" in data
    
    def test_start_capture_returns_existing_session(self, client, test_user, test_session):
        """Test that existing active session is returned"""
        response = client.post(
            "/capture/start",
            params={"username": "testuser"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["session_token"] == test_session.session_token
    
    def test_capture_status(self, client, test_user, test_session):
        """Test getting capture status"""
        response = client.get(
            "/capture/status",
            params={"username": "testuser"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "active"
        assert data["session_id"] == test_session.id
    
    def test_capture_status_no_session(self, client):
        """Test capture status when no session exists"""
        response = client.get(
            "/capture/status",
            params={"username": "nonexistent"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "inactive"
    
    def test_capture_health(self, client):
        """Test capture health endpoint"""
        response = client.get("/capture/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "capture"

class TestPredictEndpoint:
    """Test prediction endpoint"""

    def test_predict_user_specific_intrusion_after_training(self, client, test_user, test_session):
        """Prediction should use the user's own training profile."""
        training_keystrokes = [
            {"key": f"k{i}", "key_press_time": i * 120, "key_release_time": i * 120 + 50}
            for i in range(15)
        ]
        for round_num in range(3):
            response = client.post(
                "/train",
                json={
                    "username": "testuser",
                    "keystrokes": training_keystrokes,
                    "round": round_num + 1,
                }
            )
            assert response.status_code == 200

        suspicious_keystrokes = [
            {"key": f"k{i}", "key_press_time": i * 400, "key_release_time": i * 400 + 200}
            for i in range(15)
        ]
        response = client.post(
            "/predict",
            json={
                "username": "testuser",
                "session_token": test_session.session_token,
                "keystrokes": suspicious_keystrokes
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["prediction"] in ["SUSPICIOUS", "INTRUDER"]
        assert data["details"]["profile_details"]["available"] is True
    
    def test_predict_normal_behavior(self, client, test_user, test_session):
        """Test prediction on normal keystroke data"""
        keystrokes = [
            {"key": "h", "key_press_time": 0, "key_release_time": 50},
            {"key": "e", "key_press_time": 150, "key_release_time": 200},
            {"key": "l", "key_press_time": 300, "key_release_time": 350},
            {"key": "l", "key_press_time": 450, "key_release_time": 500},
            {"key": "o", "key_press_time": 600, "key_release_time": 650},
        ]
        
        response = client.post(
            "/predict",
            json={
                "username": "testuser",
                "session_token": test_session.session_token,
                "keystrokes": keystrokes
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "confidence" in data
    
    def test_predict_invalid_user(self, client, test_session):
        """Test prediction with invalid user"""
        keystrokes = [
            {"key": "a", "key_press_time": 0, "key_release_time": 50},
        ]
        
        response = client.post(
            "/predict",
            json={
                "username": "nonexistent",
                "session_token": "invalid",
                "keystrokes": keystrokes
            }
        )
        assert response.status_code == 404
    
    def test_predict_health(self, client):
        """Test predict health endpoint"""
        response = client.get("/predict/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "predict"

class TestTrainEndpoint:
    """Test training endpoint"""
    
    def test_train_user_profile(self, client, test_user):
        """Test training user profile"""
        keystrokes = [
            {"key": f"k{i}", "key_press_time": i*100, "key_release_time": i*100+50}
            for i in range(15)
        ]
        
        response = client.post(
            "/train",
            json={
                "username": "testuser",
                "keystrokes": keystrokes
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert data["sample_type"] == "phrase"
        assert data["profile_summary"]["required_rounds"] == 13

    def test_train_paragraph_sample(self, client, test_user):
        """Paragraph samples should be accepted and counted."""
        keystrokes = [
            {"key": f"k{i}", "key_press_time": i * 110, "key_release_time": i * 110 + 48}
            for i in range(22)
        ]

        response = client.post(
            "/train",
            json={
                "username": "testuser",
                "keystrokes": keystrokes,
                "round": 11,
                "sample_type": "paragraph",
                "prompt_text": "sample paragraph",
                "typed_text": "sample paragraph",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sample_type"] == "paragraph"
    
    def test_train_invalid_user(self, client):
        """Test training with invalid user"""
        keystrokes = [
            {"key": "a", "key_press_time": 0, "key_release_time": 50},
        ]
        
        response = client.post(
            "/train",
            json={
                "username": "nonexistent",
                "keystrokes": keystrokes
            }
        )
        assert response.status_code == 404
    
    def test_train_health(self, client):
        """Test train health endpoint"""
        response = client.get("/train/health")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "train"

class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_endpoint(self, client):
        """Test 404 on invalid endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
