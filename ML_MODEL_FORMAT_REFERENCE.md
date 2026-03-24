# 🤖 ML Model Input Format Reference

## **What Changed**

The backend now sends keystroke data to the ML model in the **exact format** your friend's model expects:

```python
predict_anomaly(username, features)
```

## **Input Format**

### **Feature Vector Structure**
```
[dwell1, dwell2, ..., dwellN, flight1, flight2, ..., flightN-1]
```

### **Visual Breakdown**

For a phrase with **N keystrokes**:
- **Dwell times**: N values (one for each keystroke)
- **Flight times**: N-1 values (time between consecutive keystrokes)
- **Total**: N + (N-1) = **2N - 1 values**

### **Example: "greyc laboratory"**
```
Phrase: "greyc laboratory" (16 characters)

Dwell times:   [d0, d1, d2, ..., d15]     ← 16 values
Flight times:  [f1, f2, f3, ..., f15]     ← 15 values (no f0)

Total features: 31 values ✓
```

## **Data Transformation Flow**

```
Raw Keystrokes (from Frontend)
        ↓
[{key: "g", key_press_time: 1000, key_release_time: 1050},
 {key: "r", key_press_time: 1080, key_release_time: 1130},
 ...]
        ↓
Preprocessing (validation, cleaning, outlier removal)
        ↓
Feature Extraction
  └─ Dwell time:   key_release_time - key_press_time
  └─ Flight time:  next_key_press_time - current_key_release_time
        ↓
Backend Code (extract_features_for_ml_model)
        ↓
[0.050, 0.045, ..., 0.052,      ← Dwell times (16 values)
 0.030, 0.035, ..., 0.040]      ← Flight times (15 values)
        ↓
Send to ML Model: predict_anomaly("jones", features)
        ↓
Output: "normal" or "intruder"
```

## **Backend Code Changes**

### **New Function in `services/feature_pipeline.py`**

```python
@classmethod
def extract_features_for_ml_model(cls, keystroke_batch: List[Dict[str, Any]]) -> List[float]:
    """
    Extract features in ML model format: [dwell1, dwell2, ..., dwellN, flight1, flight2, ..., flightN-1]
    
    Args:
        keystroke_batch: List of keystroke records
    
    Returns:
        Feature list in ML model format
    """
    # Extract individual dwell times for each keystroke
    dwell_times = [cls.compute_dwell_time(k) for k in keystroke_batch]
    
    # Extract individual flight times between keystrokes
    flight_times = [cls.compute_flight_time(keystroke_batch[i-1] if i > 0 else None, keystroke_batch[i]) 
                    for i in range(len(keystroke_batch))]
    
    # Remove the first flight time (before first keystroke)
    flight_times = flight_times[1:]
    
    # Concatenate: [dwell1, dwell2, ..., dwellN, flight1, flight2, ..., flightN-1]
    feature_vector = dwell_times + flight_times
    
    return feature_vector
```

## **Updated Endpoints**

### **1. Training Endpoint (`/train`)**

**Request:**
```json
{
  "username": "jones",
  "keystrokes": [
    {"key": "g", "key_press_time": 1000, "key_release_time": 1050},
    {"key": "r", "key_press_time": 1080, "key_release_time": 1130},
    ...
  ]
}
```

**Response (includes ML format):**
```json
{
  "status": "success",
  "username": "jones",
  "user_id": 2,
  "message": "Profile trained from 50 keystrokes",
  "feature_values": {
    "dwell_time": 0.050,      ← Aggregated (for display)
    "flight_time": 0.030,
    ...
  },
  "ml_model_features": {
    "dwell_count": 50,
    "flight_count": 49,
    "total_features": 99,
    "feature_vector": [0.050, 0.045, ..., 0.040]  ← CORRECT FORMAT ✓
  }
}
```

### **2. Prediction Endpoint (`/predict`)**

**Request:**
```json
{
  "username": "jones",
  "session_token": "token123",
  "keystrokes": [
    {"key": "g", "key_press_time": 1000, "key_release_time": 1050},
    ...
  ]
}
```

**Response (includes ML format info):**
```json
{
  "decision": "normal",
  "confidence": {
    "rf_probability": 0.92,
    "svm_anomaly_score": 0.15,
    "overall_confidence": 0.92
  },
  "details": {
    "keystrokes_processed": 5,
    "ml_model_input": {
      "dwell_count": 5,
      "flight_count": 4,
      "total_features": 9,
      "feature_format": "[dwell1, dwell2, ..., dwellN, flight1, flight2, ..., flightN-1]"
    }
  }
}
```

## **Important: Must Match Exactly**

✅ **Must DO:**
- Send exactly 2N-1 values (N dwells + N-1 flights)
- Dwells FIRST, then flights
- All values as floating-point numbers (milliseconds)
- Same phrase for training and testing

❌ **Must NOT DO:**
- Mix aggregate stats (mean dwell) with individual values
- Send flights before dwells
- Use different phrase for testing
- Send non-numeric values

## **Testing the Format**

### **Run Integration Test**
```bash
cd backend
python -m pytest tests/test_api.py::TestPredictEndpoint -v
```

### **Check Backend Logs**
```
ML Model Features - Dwells: 5, Flights: 4, Total: 9
Feature vector: [0.05, 0.045, 0.052, 0.048, 0.051, 0.03, 0.035, 0.032, 0.028]
```

## **Sending to Friend's ML Model**

When ready to integrate with friend's actual ML model:

```python
from your_ml_model import predict_anomaly

def predict_with_ml_model(username, features):
    """Send to friend's ML model"""
    result = predict_anomaly(username, features)
    # Result: "normal" or "intruder"
    return result

# Example usage:
features = [0.050, 0.045, ..., 0.040]  # 31 values for "greyc laboratory"
decision = predict_with_ml_model("jones", features)
print(decision)  # Output: "normal" or "intruder"
```

## **Verification Checklist**

- ✅ Using `extract_features_for_ml_model()` function
- ✅ Feature count = 2N - 1
- ✅ Dwell times first (indices 0 to N-1)
- ✅ Flight times second (indices N to 2N-2)
- ✅ All values in milliseconds (as floats)
- ✅ Training and testing use same phrase
- ✅ Backend logs show correct feature vector
- ✅ API response includes `ml_model_input` details

---

**Your backend is now sending the EXACT format your ML model expects!** 🎯
