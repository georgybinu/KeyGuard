# KeyGuard Frontend-Backend Integration Guide

**Date**: March 25, 2026  
**Status**: ✅ Frontend Updated & Integrated with Backend

---

## 🔗 Integration Overview

The frontend has been completely updated to integrate with the KeyGuard backend for real-time keystroke-based intrusion detection.

### Architecture Flow
```
Frontend (React)                 Backend (FastAPI)
    ↓                                    ↓
Input Username          →    POST /capture/start
Keystroke Capture       →    Keystroke Data Transformation
Batch Processing        →    POST /predict (Every 5 keystrokes)
Display Results         ←    Return Decision + Confidence
End Session             →    POST /capture/end
```

---

## 📊 Data Format Mapping

### Original Frontend Format → Updated Backend Format

**Before:**
```javascript
{
  key: 'a',
  keydown: 1234567890,      // Performance.now() timestamp
  keyup: 1234567940         // Performance.now() timestamp
}
```

**After (Backend Compatible):**
```javascript
{
  key: 'a',
  key_press_time: 1234567890,    // Matches backend expectation
  key_release_time: 1234567940   // Matches backend expectation
}
```

### Full Data Flow

**1. Session Initialization**
```
Frontend → Backend
POST /capture/start?username=john_doe
↓
Backend Response:
{
  "session_token": "uuid-string",
  "session_id": 123,
  "user_id": 456,
  "status": "success"
}
```

**2. Real-time Prediction (Every 5 keystrokes)**
```
Frontend → Backend
POST /predict?username=john_doe&session_token=TOKEN
Body: [
  {key_press_time: 1000, key_release_time: 1050, key: 'a'},
  {key_press_time: 1150, key_release_time: 1200, key: 'e'},
  {key_press_time: 1300, key_release_time: 1350, key: 'l'},
  {key_press_time: 1450, key_release_time: 1500, key: 'l'},
  {key_press_time: 1600, key_release_time: 1650, key: 'o'}
]
↓
Backend Response:
{
  "decision": "normal",
  "confidence": {
    "rf_probability": 0.92,
    "svm_anomaly_score": 0.75,
    "overall_confidence": 0.88
  },
  "details": {
    "keystrokes_processed": 5,
    "features": {
      "dwell_time": 50.0,
      "flight_time": 100.0,
      ...
    }
  }
}
```

**3. Session Termination**
```
Frontend → Backend
POST /capture/end?username=john_doe&session_token=TOKEN
↓
Backend Response:
{
  "status": "success",
  "message": "Capture session ended",
  "session_id": 123
}
```

---

## 🎨 UI Changes

### Before
- ❌ No username input
- ❌ No session management
- ❌ No real-time predictions
- ❌ Only local keystroke display
- ❌ Download button only

### After
- ✅ Username input field
- ✅ Session start/end buttons
- ✅ Real-time intrusion detection results
- ✅ Color-coded decision display (green/yellow/red)
- ✅ Backend API integration
- ✅ Confidence score visualization

### New UI Components

**Session Setup Panel**
```
┌─────────────────────────────────────┐
│  Start Keystroke Analysis           │
├─────────────────────────────────────┤
│  [Enter username...............] ✓  │
│  [Start Session Button]             │
└─────────────────────────────────────┘
```

**Prediction Result Card**
```
┌──────────────────────────────────────┐
│ 🔒 Intrusion Detection               │
├──────────────────────────────────────┤
│ Decision: NORMAL                     │
├──────────────────────────────────────┤
│ Confidence Scores:                   │
│  RF: 92.5%   SVM: 75.0%   Ovr: 88%  │
└──────────────────────────────────────┘
```

### Decision Color Coding
- 🟢 **Green (Normal)**: Normal behavior detected
- 🟡 **Yellow (Suspicious)**: Behavior deviates from baseline
- 🔴 **Red (Intrusion)**: Anomalous behavior detected

---

## 🔑 Key State Management

### Frontend State Variables

```javascript
// Session Management
const [username, setUsername] = useState('')          // User identifier
const [sessionStarted, setSessionStarted] = useState(false) // Session active?
const [sessionToken, setSessionToken] = useState(null)      // Auth token
const [sessionId, setSessionId] = useState(null)            // Session ID

// Keystroke Capture
const [typed, setTyped] = useState('')                 // Text typed so far
const [keystrokes, setKeystrokes] = useState([])       // All keystrokes
const [keystrokeBuffer, setKeystrokeBuffer] = useState([]) // Batch (5 keys)

// Prediction Results
const [predictionResult, setPredictionResult] = useState(null) // Latest result
const [loading, setLoading] = useState(false)          // API loading state
const [error, setError] = useState(null)               // Error messages
```

---

## 🔄 Event Flow

### 1. User Enters Username and Starts Session

```
User clicks "Start Session"
    ↓
Frontend validates username not empty
    ↓
Frontend calls: POST /capture/start?username=john
    ↓
Backend creates session, returns token
    ↓
Frontend stores session_token & session_id
    ↓
UI switches to typing interface
```

### 2. User Types (Real-time Processing)

```
User presses key (onKeyDown)
    ↓
Record key_press_time (performance.now())
    ↓
User releases key (onKeyUp)
    ↓
Record key_release_time, create keystroke object
    ↓
Add to keystrokeBuffer
    ↓
If keystrokeBuffer.length >= 5:
  ├─ Transform keystroke format
  ├─ Send to: POST /predict (with username & session_token)
  ├─ Receive decision + confidence scores
  ├─ Update UI with prediction result
  └─ Clear keystrokeBuffer
```

### 3. User Ends Session

```
User clicks "End Session"
    ↓
Frontend calls: POST /capture/end (with username & session_token)
    ↓
Backend closes session, logs any intrusions
    ↓
Frontend resets all state
    ↓
UI returns to session setup
```

---

## 🔧 Configuration

### Backend URL
**File**: `frontend/src/App.jsx`  
**Variable**: `BACKEND_URL`  
**Default**: `http://localhost:8000`

To connect to different backend:
```javascript
const BACKEND_URL = 'http://your-server:8000'
// Or for production:
const BACKEND_URL = 'https://api.keyguard.com'
```

### Test Paragraph
**File**: `frontend/src/App.jsx`  
**Variable**: `PARAGRAPH`  
```javascript
const PARAGRAPH = "I start my day with a cup of tea and check my phone for a few minutes. It is a simple routine, but it helps me get ready for the day."
```

### Batch Size (Number of Keystrokes Before Prediction)
**File**: `frontend/src/App.jsx`  
**Location**: `handleKeyUp()` function

Currently set to 5 keystrokes:
```javascript
if (newBuffer.length >= 5) {
  sendPrediction(transformedKeystrokes)
}
```

To change: Edit the condition to use different number.

---

## 📋 Function Reference

### Session Management

**`startSession()`**
- Validates username
- Calls `/capture/start` endpoint
- Stores session credentials
- Handles errors gracefully

**`endSession()`**
- Calls `/capture/end` endpoint
- Clears session data
- Triggered on "End Session" click

### Keystroke Processing

**`handleKeyDown(e)`**
- Records key press timestamp
- Validates session is active
- Stores in activeKeysRef

**`handleKeyUp(e)`**
- Records key release timestamp
- Creates keystroke object
- Adds to buffer for batching
- Triggers prediction at batch size

**`transformKeystroke(keystroke)`**
- Converts frontend format to backend format
- Maps `keydown` → `key_press_time`
- Maps `keyup` → `key_release_time`

### API Communication

**`sendPrediction(keystrokeData)`**
- Sends keystroke batch to `/predict`
- Includes username & session_token
- Updates UI with prediction result
- Handles network errors

### Utilities

**`prepareBackendData()`**
- Formats complete session data
- Used for download functionality
- Includes all metadata

**`downloadData()`**
- Creates JSON file of session
- Triggers browser download
- Filename: `keystrokes-{timestamp}.json`

---

## 🧪 Testing the Integration

### Prerequisites
1. ✅ Backend running: `python app.py`
2. ✅ Backend accessible at `http://localhost:8000`
3. ✅ Frontend running: `npm run dev`

### Test Steps

**1. Start Backend**
```bash
cd backend
python app.py
# Expected: Uvicorn running on http://0.0.0.0:8000
```

**2. Start Frontend**
```bash
cd frontend
npm run dev
# Expected: Vite running on http://localhost:5173
```

**3. Test Session Flow**
- Open browser: http://localhost:5173
- Enter username: "test_user"
- Click "Start Session"
- ✅ Should see session info displayed
- Type a few characters
- ✅ After 5+ keystrokes, should see prediction result
- Check if decision is displayed (should be "normal" for normal typing)

**4. Test Error Handling**
- Try starting session without username → Error message
- Check browser console for API calls
- Verify requests are being sent to backend

---

## 🐛 Troubleshooting

### Issue: "Failed to connect" error
**Cause**: Backend not running  
**Solution**: 
```bash
cd backend
python app.py
```

### Issue: No prediction results showing
**Cause**: Batch size not reached (need 5+ keystrokes)  
**Solution**: Type more characters

### Issue: Username field not appearing
**Cause**: JavaScript error or file not saved  
**Solution

**:
```bash
# Clear cache and restart
npm run dev
```

### Issue: CORS errors in console
**Cause**: Backend CORS configuration  
**Solution**: Check backend `app.py` CORS middleware is enabled:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specific frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Keystrokes not recording
**Cause**: Input field disabled or session not started  
**Solution**: Start session first (enter username and click Start)

---

## 📊 API Response Examples

### Successful Prediction - Normal
```json
{
  "decision": "normal",
  "confidence": {
    "rf_probability": 0.95,
    "svm_anomaly_score": 0.82,
    "overall_confidence": 0.91
  },
  "details": {
    "keystrokes_processed": 5,
    "features": {
      "dwell_time": 48.5,
      "flight_time": 105.2,
      "key_press_rate": 4.8,
      "key_release_interval": 112.5,
      "typing_speed": 48.5
    },
    "decision_factors": [
      "RF: High confidence in normal (prob=0.95)",
      "SVM: Normal behavior detected"
    ]
  }
}
```

### Suspicious Behavior
```json
{
  "decision": "suspicious",
  "confidence": {
    "rf_probability": 0.45,
    "svm_anomaly_score": 0.32,
    "overall_confidence": 0.65
  },
  "details": {
    "keystrokes_processed": 5,
    "decision_factors": [
      "RF: Suspicious behavior (prob=0.45)",
      "SVM: Normal behavior detected"
    ]
  }
}
```

### Intrusion Detected
```json
{
  "decision": "intrusion",
  "confidence": {
    "rf_probability": 0.25,
    "svm_anomaly_score": -0.75,
    "overall_confidence": 0.85
  },
  "details": {
    "keystrokes_processed": 5,
    "decision_factors": [
      "RF: Low confidence in normal (prob=0.25)",
      "SVM: Anomaly detected (score=-0.75)"
    ]
  }
}
```

---

## ✅ Integration Checklist

- ✅ Frontend captures keystrokes with timestamps
- ✅ Frontend transforms data to backend format
- ✅ Frontend sends username to backend
- ✅ Frontend starts session and gets token
- ✅ Frontend sends real-time predictions (every 5 keystrokes)
- ✅ Frontend displays decision results
- ✅ Frontend shows confidence scores
- ✅ Frontend ends session properly
- ✅ CSS styled for new UI components
- ✅ Error handling implemented
- ✅ Loading states managed

---

## 📝 Summary

### What Changed
1. **Added Session Management**: Username input + session token handling
2. **Updated Data Format**: Frontend now matches backend keystroke format
3. **Real-time Predictions**: Sends data every 5 keystrokes
4. **Result Display**: Shows decision + confidence scores with color coding
5. **Enhanced UI**: New sections for setup and prediction results
6. **API Integration**: All operations connected to backend endpoints

### How It Works
1. User enters username and starts session
2. Frontend gets session token from backend
3. As user types, frontend captures keystrokes
4. Every 5 keystrokes, frontend sends batch to `/predict` endpoint
5. Backend returns decision (normal/suspicious/intrusion)
6. Frontend displays result with color coding
7. When done, user clicks "End Session" to close

### Compatibility
- ✅ React 19.2.4
- ✅ Modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ No breaking changes to existing code
- ✅ Backward compatible keystroke collection

---

**Status**: 🟢 **READY FOR TESTING**  
**Frontend-Backend Integration**: ✅ Complete  
**All Tests**: Pending on actual server connection  

---
