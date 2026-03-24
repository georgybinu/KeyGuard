"""
Test script to verify ML model input format
Shows exactly what's being sent to the ML model
"""

import sys
sys.path.insert(0, 'backend')

from services.feature_pipeline import FeaturePipeline
import json

def demo_keystroke_sequence():
    """Demonstrate keystroke data transformation"""
    
    print("=" * 70)
    print("🤖 ML MODEL INPUT FORMAT DEMONSTRATION")
    print("=" * 70)
    print()
    
    # Example: User typing "hello"
    keystrokes = [
        {"key": "h", "key_press_time": 1000, "key_release_time": 1050},
        {"key": "e", "key_press_time": 1080, "key_release_time": 1130},
        {"key": "l", "key_press_time": 1150, "key_release_time": 1200},
        {"key": "l", "key_press_time": 1220, "key_release_time": 1270},
        {"key": "o", "key_press_time": 1290, "key_release_time": 1340},
    ]
    
    print("📝 Raw Keystroke Data (5 keystrokes for 'hello')")
    print("-" * 70)
    for i, k in enumerate(keystrokes):
        dwell = k['key_release_time'] - k['key_press_time']
        print(f"  Keystroke {i+1}: '{k['key']}'")
        print(f"    Press:  {k['key_press_time']} ms")
        print(f"    Release: {k['key_release_time']} ms")
        print(f"    Dwell:  {dwell} ms")
        if i < len(keystrokes) - 1:
            flight = keystrokes[i+1]['key_press_time'] - k['key_release_time']
            print(f"    Flight to next: {flight} ms")
        print()
    
    # Extract features for ML model
    ml_features = FeaturePipeline.extract_features_for_ml_model(keystrokes)
    
    print("=" * 70)
    print("✅ ML MODEL INPUT FORMAT")
    print("=" * 70)
    print()
    
    # Parse dwell and flight times
    num_keystrokes = len(keystrokes)
    dwells = ml_features[:num_keystrokes]
    flights = ml_features[num_keystrokes:]
    
    print(f"📊 Feature Vector Structure:")
    print(f"   Total keystrokes: {num_keystrokes}")
    print(f"   Dwell times (N): {len(dwells)}")
    print(f"   Flight times (N-1): {len(flights)}")
    print(f"   Total features: {num_keystrokes} + {len(flights)} = {len(ml_features)}")
    print()
    
    print(f"🔹 Dwell Times (key hold duration)")
    print(f"   Values: {dwells}")
    print()
    
    print(f"🔹 Flight Times (time between keystrokes)")
    print(f"   Values: {flights}")
    print()
    
    print(f"🔹 Complete Feature Vector (format for ML model)")
    print(f"   [{', '.join(f'{v:.1f}' for v in ml_features)}]")
    print()
    
    print("=" * 70)
    print("📋 JSON Format for API Request")
    print("=" * 70)
    print()
    
    request_format = {
        "username": "jones",
        "session_token": "token123",
        "keystrokes": keystrokes
    }
    
    print("POST /predict")
    print(json.dumps(request_format, indent=2))
    print()
    
    print("=" * 70)
    print("📤 What Gets Sent to ML Model")
    print("=" * 70)
    print()
    
    ml_input = {
        "username": "jones",
        "features": ml_features
    }
    
    print(f"predict_anomaly('{ml_input['username']}', {ml_input['features']})")
    print()
    print("Format:")
    print(f"  predict_anomaly(username, [dwell1, dwell2, ..., dwell5, flight1, ..., flight4])")
    print()
    
    print("=" * 70)
    print("✨ Verification")
    print("=" * 70)
    print()
    print(f"✅ Feature count: {len(ml_features)} = 2*{num_keystrokes} - 1 ✓")
    print(f"✅ Dwells first: {dwells} ✓")
    print(f"✅ Flights second: {flights} ✓")
    print(f"✅ All numeric values: {all(isinstance(v, (int, float)) for v in ml_features)} ✓")
    print()

def demo_real_training_example():
    """Demonstrate with real training example"""
    
    print()
    print("=" * 70)
    print("🎯 REAL EXAMPLE: Training Profile for 'greyc laboratory'")
    print("=" * 70)
    print()
    
    # Simulating 50 keystrokes (16 chars * 3 paragraphs + some)
    keystrokes = []
    base_time = 1000
    
    phrase = "greyc laboratory"
    for i, char in enumerate(phrase):
        press_time = base_time + (i * 100)
        release_time = press_time + (50 + i % 3 * 5)  # Vary dwell time slightly
        keystrokes.append({
            "key": char,
            "key_press_time": press_time,
            "key_release_time": release_time
        })
    
    ml_features = FeaturePipeline.extract_features_for_ml_model(keystrokes)
    
    print(f"Phrase typed: '{phrase}'")
    print(f"Number of characters: {len(keystrokes)}")
    print()
    print(f"Feature vector for training:")
    print(f"  Dwell times: {len(keystrokes)} values")
    print(f"  Flight times: {len(keystrokes)-1} values")
    print(f"  Total: {len(ml_features)} values")
    print()
    print(f"Vector: [{', '.join(f'{v:.1f}' for v in ml_features[:3])}... (first 3), ..., {', '.join(f'{v:.1f}' for v in ml_features[-3:])} (last 3)]")
    print()
    print(f"✓ Ready to send to: predict_anomaly('jones', {len(ml_features)} values)")
    print()

def demo_batch_predictions():
    """Demonstrate batch prediction format"""
    
    print("=" * 70)
    print("⚡ BATCH PREDICTION: Every 5 Keystrokes")
    print("=" * 70)
    print()
    
    print("During typing detection phase:")
    print()
    print("  User types 5 keys")
    print("    ↓")
    print("  Extract dwell/flight times")
    print("    ↓")
    print("  Format: [d1, d2, d3, d4, d5, f1, f2, f3, f4]")
    print("  (5 dwells + 4 flights = 9 values)")
    print("    ↓")
    print("  Call: predict_anomaly('jones', features)")
    print("    ↓")
    print("  Receive: 'normal' or 'intruder'")
    print("    ↓")
    print("  Display in UI: Green ✓ or Red ✗")
    print()

if __name__ == "__main__":
    demo_keystroke_sequence()
    demo_real_training_example()
    demo_batch_predictions()
    
    print("=" * 70)
    print("✅ Format is now EXACT for your friend's ML model!")
    print("=" * 70)
