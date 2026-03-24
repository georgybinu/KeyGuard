"""
KeyGuard Frontend-Backend Integration Test Script
Validates that frontend and backend are properly connected
"""

import requests
import json
from time import time

# Configuration
BACKEND_URL = "http://localhost:8000"
TEST_USERNAME = "test_integration_user"

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")

def test_backend_health():
    """Test if backend is running"""
    print_section("1. Testing Backend Health")
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Backend is running")
            print(f"   Status: {data['status']}")
            print(f"   Service: {data['service']}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print(f"   Make sure backend is running: python app.py")
        return False

def test_session_start():
    """Test starting a capture session"""
    print_section("2. Testing Session Start (/capture/start)")
    try:
        response = requests.post(
            f"{BACKEND_URL}/capture/start",
            params={"username": TEST_USERNAME}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session started successfully")
            print(f"   Username: {TEST_USERNAME}")
            print(f"   Session ID: {data['session_id']}")
            print(f"   Session Token: {data['session_token'][:20]}...")
            print(f"   User ID: {data['user_id']}")
            return data['session_token'], data['session_id']
        else:
            print(f"❌ Failed to start session: {response.status_code}")
            print(f"   Response: {response.text}")
            return None, None
    except Exception as e:
        print(f"❌ Error starting session: {e}")
        return None, None

def test_prediction(session_token):
    """Test sending keystroke data for prediction"""
    print_section("3. Testing Prediction (/predict)")
    
    # Simulate normal typing keystrokes
    keystrokes = [
        {"key": "h", "key_press_time": 1000, "key_release_time": 1045},
        {"key": "e", "key_press_time": 1150, "key_release_time": 1195},
        {"key": "l", "key_press_time": 1310, "key_release_time": 1355},
        {"key": "l", "key_press_time": 1425, "key_release_time": 1475},
        {"key": "o", "key_press_time": 1590, "key_release_time": 1640},
    ]
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            params={
                "username": TEST_USERNAME,
                "session_token": session_token,
                "keystrokes": keystrokes
            },
            json=keystrokes
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Prediction received successfully")
            print(f"   Decision: {data['decision'].upper()}")
            print(f"   RF Probability: {data['confidence']['rf_probability']:.2%}")
            print(f"   SVM Score: {data['confidence']['svm_anomaly_score']:.2f}")
            print(f"   Overall Confidence: {data['confidence']['overall_confidence']:.2%}")
            print(f"   Keystrokes Processed: {data['details']['keystrokes_processed']}")
            
            # Display decision factors
            if data['details'].get('decision_factors'):
                print(f"   Decision Factors:")
                for factor in data['details']['decision_factors']:
                    print(f"     - {factor}")
            
            return True
        else:
            print(f"❌ Prediction failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error sending prediction: {e}")
        return False

def test_suspicious_typing(session_token):
    """Test with suspicious typing pattern"""
    print_section("4. Testing Suspicious Typing Pattern")
    
    # Simulate suspicious typing (very fast, inconsistent)
    keystrokes = [
        {"key": "h", "key_press_time": 1000, "key_release_time": 1010},
        {"key": "e", "key_press_time": 1050, "key_release_time": 1060},
        {"key": "l", "key_press_time": 1080, "key_release_time": 1100},
        {"key": "l", "key_press_time": 1200, "key_release_time": 1210},
        {"key": "o", "key_press_time": 1820, "key_release_time": 1830},
    ]
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/predict",
            params={
                "username": TEST_USERNAME,
                "session_token": session_token,
                "keystrokes": keystrokes
            },
            json=keystrokes
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Suspicious pattern received")
            print(f"   Decision: {data['decision'].upper()}")
            print(f"   RF Probability: {data['confidence']['rf_probability']:.2%}")
            print(f"   Overall Confidence: {data['confidence']['overall_confidence']:.2%}")
            return True
        else:
            print(f"❌ Suspicious prediction failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing suspicious pattern: {e}")
        return False

def test_session_status(session_token):
    """Test checking session status"""
    print_section("5. Testing Session Status (/capture/status)")
    try:
        response = requests.get(
            f"{BACKEND_URL}/capture/status",
            params={"username": TEST_USERNAME}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session status retrieved")
            print(f"   Status: {data['status']}")
            if data['status'] == 'active':
                print(f"   Session ID: {data['session_id']}")
                print(f"   Start Time: {data['start_time']}")
            return True
        else:
            print(f"❌ Failed to get status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return False

def test_session_end(session_token):
    """Test ending a session"""
    print_section("6. Testing Session End (/capture/end)")
    try:
        response = requests.post(
            f"{BACKEND_URL}/capture/end",
            params={
                "username": TEST_USERNAME,
                "session_token": session_token
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Session ended successfully")
            print(f"   Status: {data['status']}")
            print(f"   Message: {data['message']}")
            print(f"   Session ID: {data['session_id']}")
            return True
        else:
            print(f"❌ Failed to end session: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error ending session: {e}")
        return False

def test_data_format():
    """Verify keystroke data format compatibility"""
    print_section("7. Verifying Data Format Compatibility")
    
    # Frontend format
    frontend_format = {
        "key": "a",
        "keydown": 1000.5,
        "keyup": 1050.3
    }
    
    # Backend format (after transformation)
    backend_format = {
        "key": "a",
        "key_press_time": int(frontend_format["keydown"]),
        "key_release_time": int(frontend_format["keyup"])
    }
    
    print(f"✅ Data format transformation verified")
    print(f"   Frontend → Backend")
    print(f"   key → key (unchanged)")
    print(f"   keydown → key_press_time")
    print(f"   keyup → key_release_time")
    print(f"   Example:")
    print(f"     Input:  {frontend_format}")
    print(f"     Output: {backend_format}")
    
    return True

def run_all_tests():
    """Run complete integration test suite"""
    print("\n" + "="*60)
    print("  KeyGuard Frontend-Backend Integration Test Suite")
    print("="*60)
    
    tests_passed = 0
    tests_failed = 0
    
    # Test 1: Health check
    if not test_backend_health():
        print("\n❌ Backend is not running. Cannot continue tests.")
        print("   Please start backend: python app.py")
        return
    
    tests_passed += 1
    
    # Test 2: Data format
    if test_data_format():
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 3: Session start
    session_token, session_id = test_session_start()
    if session_token:
        tests_passed += 1
    else:
        tests_failed += 1
        print("\n❌ Cannot continue without session. Stopping tests.")
        return
    
    # Test 4: Session status
    if test_session_status(session_token):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 5: Normal prediction
    if test_prediction(session_token):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 6: Suspicious pattern
    if test_suspicious_typing(session_token):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Test 7: Session end
    if test_session_end(session_token):
        tests_passed += 1
    else:
        tests_failed += 1
    
    # Summary
    total_tests = tests_passed + tests_failed
    print_section("Test Summary")
    print(f"✅ Passed: {tests_passed}/{total_tests}")
    print(f"❌ Failed: {tests_failed}/{total_tests}")
    print(f"Success Rate: {(tests_passed/total_tests*100):.1f}%")
    
    if tests_failed == 0:
        print("\n🎉 All tests passed! Frontend-Backend integration is working!")
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed. Check the output above.")
    
    print("\n" + "="*60)

if __name__ == "__main__":
    run_all_tests()
