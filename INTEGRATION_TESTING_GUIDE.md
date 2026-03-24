# 🚀 KeyGuard Integration Testing Guide

## Quick Start - Run Both Servers

### Terminal 1: Start Backend Server
```bash
cd backend
python app.py
```

Expected output:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Start Frontend Server
```bash
cd frontend
npm run dev
```

Expected output:
```
  VITE v8.0.1  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

## Test Scenarios

### 1. **Browser Integration Test** (Manual)

1. Open `http://localhost:5173` in your browser
2. **Session Setup Screen** should appear:
   - Text input for username (try: `test_user`)
   - "Start Session" button
3. **Click "Start Session"**
   - Backend receives: `POST /capture/start?username=test_user`
   - Frontend stores: session_token, session_id
   - UI switches to typing interface
4. **Type normally** (e.g., "hello world")
   - Every keystroke is captured
   - Every 5 keystrokes trigger prediction:
     - Frontend sends: `POST /predict` with transformed keystroke data
     - Backend returns: decision (NORMAL/SUSPICIOUS/INTRUSION) + confidence scores
   - Prediction card appears on screen:
     - 🟢 Green = Normal behavior
     - 🟡 Yellow = Suspicious behavior
     - 🔴 Red = Intrusion detected
5. **Check Browser DevTools**
   - Open Network tab (F12 → Network)
   - See API calls:
     - `capture/start` (1 call)
     - `predict` (called every 5 keystrokes)
6. **End Session**
   - Click "End Session" button
   - Backend receives: `POST /capture/end`

✅ **Success Indicators:**
- Prediction cards appear while typing
- Color changes based on behavior (green → yellow/red)
- Confidence scores displayed (0-100%)
- No console errors

### 2. **API Integration Test** (Automated)

```bash
# Make sure both backend and frontend are running first!
python test_integration.py
```

This script tests all API endpoints:
1. ✅ Backend health check
2. ✅ Data format compatibility
3. ✅ Session start
4. ✅ Session status
5. ✅ Normal keystroke prediction
6. ✅ Suspicious pattern detection
7. ✅ Session end

Expected output: **All tests passed! ✅**

## Data Flow Verification

### Frontend → Backend Transformation

**Frontend Keystroke Object:**
```javascript
{
  key: "a",
  keydown: 1234567.890,    // performance.now() timestamp
  keyup: 1234612.340
}
```

**Backend Keystroke Object (after transformation):**
```json
{
  "key": "a",
  "key_press_time": 1234567,     // Converted to int
  "key_release_time": 1234612
}
```

### Prediction Response

**Backend Response Format:**
```json
{
  "decision": "normal",
  "confidence": {
    "rf_probability": 0.95,
    "svm_anomaly_score": 0.12,
    "overall_confidence": 0.92
  },
  "details": {
    "keystrokes_processed": 5,
    "decision_factors": [
      "dwell_time_normal",
      "typing_speed_consistent",
      "key_release_interval_stable"
    ]
  }
}
```

## Browser Console - DevTools Debugging

### Check API Calls
1. Open DevTools: `F12`
2. Go to **Network** tab
3. Type some characters and watch:
   - `POST capture/start` → 1 call at start
   - `POST predict` → Called every 5 keystrokes
4. Click each request to see:
   - Request body (keystrokes sent)
   - Response body (prediction decision)
   - Status code (should be 200)

### Check Frontend Console Logs
1. Go to **Console** tab
2. You should see logs like:
   ```
   ✅ Session started successfully
   ✅ Prediction received: normal (95% confidence)
   ✅ Session ended
   ```
3. If errors appear, check:
   - Backend is running on port 8000
   - Frontend is running on port 5173
   - No typos in API URLs

## Common Issues & Solutions

### ❌ "Cannot connect to backend"
**Problem:** Frontend can't reach backend API
```
Error: Failed to fetch - http://localhost:8000/capture/start
```

**Solution:**
1. Verify backend is running: `python app.py` in backend folder
2. Check backend port is 8000 in App.jsx: `BACKEND_URL = 'http://localhost:8000'`
3. Restart both servers

### ❌ "Session token invalid"
**Problem:** Backend rejects session token
```json
{"detail": "Invalid or expired session token"}
```

**Solution:**
1. Start a new session (token expired after ~30 min)
2. Check token is included in API call headers
3. Verify same username is used for start and predict calls

### ❌ No predictions appearing
**Problem:** Predictions not showing on frontend
```
Typed 5+ keys but no prediction card appeared
```

**Solution:**
1. Check Network tab: Is `POST predict` being called?
   - If NO: keystroke handler might be failing
   - If YES: response might not be displayed correctly
2. Check Console for errors
3. Verify session token is active (should see "Session Active" info)

### ❌ "Keystroke batch incomplete"
**Problem:** Backend says keystrokes aren't processing
```json
{"detail": "Expecting 5 keystrokes, got X"}
```

**Solution:**
1. Type exactly 5 keystrokes before prediction is sent
2. Check keystroke format in Network tab matches backend expectation:
   ```json
   [
     {"key": "a", "key_press_time": 1234567, "key_release_time": 1234612},
     ...
   ]
   ```

## Expected Test Duration

- Backend startup: ~2 seconds
- Frontend startup: ~3 seconds
- API integration test: ~5 seconds
- **Total: ~10 seconds**

## Next Steps After Validation

✅ **If all tests pass:**
1. System is production-ready
2. Deploy backend to cloud server
3. Update frontend BACKEND_URL to production endpoint
4. Deploy frontend to static hosting (AWS S3, Azure Blob, etc.)

🔧 **If tests fail:**
1. Check console errors (browser DevTools)
2. Check backend logs (terminal where app.py runs)
3. Review API responses in Network tab
4. Compare keystroke format to expected schema

## 📊 Performance Metrics

Once running, you can check:
- **Backend response time:** Should be <50ms per prediction
- **Frontend UI updates:** Should be <100ms
- **Network latency:** Check Network tab → Timing → Duration

---

**You have a fully integrated real-time keystroke analysis system! 🎯**

For more details see: [FRONTEND_BACKEND_INTEGRATION.md](./FRONTEND_BACKEND_INTEGRATION.md)
