# KeyGuard Frontend - Complete Demo Guide

## Overview

This is a fully functional React + Vite frontend for the KeyGuard keystroke authentication system. The frontend provides:

1. **User Registration** - Create a user profile with keystroke baseline
2. **Keystroke Training** - Capture 10 rounds of keystroke data (phrase: "greyc laboratory")
3. **Test Cases** - Run 5 different test scenarios to demonstrate detection:
   - Legitimate User (Normal Typing) → Expected: NORMAL
   - Slow Intruder → Expected: INTRUDER
   - Fast Intruder → Expected: INTRUDER
   - Hesitant Intruder (Long pauses) → Expected: INTRUDER
   - Inconsistent Intruder (Variable speed) → Expected: INTRUDER
4. **Dashboard** - View user profile stats, training status, and test results

## Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Register.jsx          # User registration component
│   │   ├── Capture.jsx           # Keystroke training (10 rounds)
│   │   ├── TestCases.jsx         # Test scenario execution
│   │   └── Dashboard.jsx         # User stats & profile display
│   ├── styles/
│   │   ├── Register.css          # Registration styling
│   │   ├── Capture.css           # Training interface styling
│   │   ├── TestCases.css         # Test cases UI styling
│   │   └── Dashboard.css         # Dashboard styling
│   ├── App.jsx                   # Main app with navigation
│   ├── App.css                   # Main app styling
│   ├── main.jsx                  # Entry point
│   └── index.css                 # Global styles
├── package.json
├── vite.config.js
└── Dockerfile
```

## Setup Instructions

### Prerequisites
- Node.js 16+ and npm
- Backend running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

The frontend will start on `http://localhost:5173`

### Build for Production

```bash
npm run build
```

## Features

### 1. User Registration Page
- Username, Email, Phone, Password input
- Form validation
- Displays KeyGuard information and features
- Transitions to training upon successful registration

### 2. Keystroke Training (Capture Page)
- **Phase 1 (Ready):** Instructions and start button
- **Phase 2 (Training):** 
  - Type phrase "greyc laboratory" exactly
  - Progress bar shows rounds (1-10)
  - Real keystroke tracking (keydown/keyup events)
  - Phrase match validation
- **Phase 3 (Completed):** Summary stats and next steps

**Key measurements:**
- Dwell Time: How long each key is held
- Flight Time: Gap between releasing one key and pressing next
- Typing Speed: Overall typing rhythm
- Key Intervals: Time patterns between keystrokes

### 3. Test Cases Page
- **Test Selection:** 5 different scenarios to run
- **Test Execution:** Type the required phrase for each test
- **Results Display:** 
  - Test status (PASSED/FAILED)
  - Prediction from backend (NORMAL or INTRUDER)
  - Confidence scores
  - Feature analysis (dwell time, flight time, typing speed, keystroke count)

**Test Scenarios:**

| Test | Description | Expected | What It Shows |
|------|-------------|----------|---------------|
| Legitimate User | Type naturally at normal speed | NORMAL | Baseline behavior |
| Slow Intruder | Type slowly and deliberately | INTRUDER | Detection of timing anomalies |
| Fast Intruder | Type very quickly and erratically | INTRUDER | Speed pattern recognition |
| Hesitant Intruder | Type with long pauses between keys | INTRUDER | Pause pattern detection |
| Inconsistent Intruder | Type with variable speed/pauses | INTRUDER | Rhythm consistency checking |

### 4. Dashboard
- **User Profile:** Username, email, phone, registration date
- **Training Status:** Rounds completed, profile status
- **Detection Statistics:** Total tests, successful tests, accuracy percentage
- **Feature Profile:** Average dwell time, flight time, typing speed, keystroke count
- **Activity Log:** Recent test results with timestamps
- **System Information:** How KeyGuard detection works

### Navigation
- Header navigation appears after login
- Links: Training → Test Cases → Dashboard
- Can switch between pages freely after training
- Logout button returns to registration

## API Integration

The frontend communicates with the backend using these endpoints:

### POST /register
Register a new user
```json
{
  "username": "user1",
  "email": "user@example.com",
  "phone": "1234567890",
  "password": "password"
}
```

### POST /train
Submit keystroke data for training
```json
{
  "username": "user1",
  "keystrokes": [...],
  "round": 1
}
```

### POST /predict
Get prediction for keystroke data
```json
{
  "username": "user1",
  "keystrokes": [...]
}
```

## Demo Flow

1. **Start:** Click "Create Profile" after entering username, email, phone, password
2. **Register:** Form validates and creates user in backend
3. **Train:** Type "greyc laboratory" 10 times to create baseline profile
4. **Test:** Run 5 different test scenarios
   - First 4 should be detected as intruders (not matching your normal typing)
   - You can re-run tests to see results
5. **Dashboard:** View your statistics and profile information

## Styling

- **Color Scheme:** Purple/blue gradient theme
- **Components:** Responsive card-based layout
- **Animations:** Smooth transitions and hover effects
- **Responsive:** Works on desktop, tablet, and mobile

Key CSS features:
- Gradient backgrounds
- Progress bars and status indicators
- Form validation styling
- Card-based UI with shadows
- Responsive grid layouts

## Environment Variables

If needed, you can configure:
```javascript
// In App.jsx or component files
const BACKEND_URL = 'http://localhost:8000'
```

## Troubleshooting

### "Connection error" on registration
- Make sure backend is running on port 8000
- Check CORS settings on backend

### "Make sure backend is running" during training
- Backend should be at `http://localhost:8000`
- Run: `cd backend && python app.py`

### Training not progressing
- Type the exact phrase: "greyc laboratory"
- Check browser console for error messages
- Ensure keystroke events are being captured

### Test results not showing
- Backend must be running
- Ensure you've completed training first
- Check backend is returning valid predictions

## Performance Tips

- Uses React hooks for state management
- Lazy loading of pages through navigation
- CSS animations use GPU acceleration
- Keystroke events throttled appropriately
- Efficient event listener cleanup

## Browser Compatibility

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

- Real-time statistics during training
- Export profile data
- Biometric analysis graphs
- Multi-device support
- Advanced authentication options

---

**Built with React 19.x + Vite 8.x**
**Backend: FastAPI + Scikit-learn**
**ML Models: One-Class SVM + Random Forest**
