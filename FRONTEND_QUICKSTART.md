# Quick Start - KeyGuard Frontend Demo

## Prerequisites

- **Node.js 16+** and npm installed
- **Backend running** on `http://localhost:8000`

## Installation & Running

### Option 1: Using the Demo Script (Recommended)

```bash
# From KeyGuard root directory
chmod +x run-keyguard-demo.sh
./run-keyguard-demo.sh
```

This will:
1. Start the FastAPI backend on port 8000
2. Start the React frontend on port 5173
3. Open your browser automatically
4. Show you the complete demo flow

### Option 2: Manual Setup

#### Step 1: Start Backend

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Backend will run on `http://localhost:8000`

#### Step 2: Start Frontend

In a new terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend will open at `http://localhost:5173`

## Demo Walkthrough

### 1. Register (2-3 minutes)

- **Username:** e.g., "john_doe"
- **Email:** e.g., "john@example.com"
- **Phone:** e.g., "123-456-7890"
- **Password:** Any password (for demo purposes)
- Click "Create Profile"

### 2. Keystroke Training (5-10 minutes)

- **Phase 1:** Read the instructions and click "Start Training Session"
- **Phase 2:** Type the phrase **"greyc laboratory"** exactly as shown
  - 10 rounds total
  - Progress bar shows: Round 1-10
  - Type naturally at your normal speed
  - Must match exactly (case-sensitive, including space)
- **Phase 3:** System shows "Training Complete!"

### 3. Test Cases (5-10 minutes)

Run each of the 5 test scenarios:

1. **Legitimate User (Normal)** - Type naturally
   - Expected: NORMAL ✅
   - This should match your training profile

2. **Slow Intruder** - Type slowly and deliberately
   - Expected: INTRUDER 🚨
   - Demonstrates detection of timing anomalies

3. **Fast Intruder** - Type very quickly and erratically  
   - Expected: INTRUDER 🚨
   - Shows speed pattern recognition

4. **Hesitant Intruder** - Type with long pauses between keys
   - Expected: INTRUDER 🚨
   - Demonstrates pause detection

5. **Inconsistent Intruder** - Type with variable speed
   - Expected: INTRUDER 🚨
   - Shows rhythm consistency checking

For each test:
- View the test description
- Type the required phrase
- Click "Run Test"
- See the prediction and confidence scores
- Feature breakdown shows: Dwell Time, Flight Time, Typing Speed, Keystroke Count

### 4. Dashboard

View your profile statistics:
- Username, email, phone, registration date
- Training status (10/10 rounds complete)
- Detection statistics (test results, accuracy)
- Feature profile (typing characteristics)
- Activity log (recent tests)
- System information about how KeyGuard works

## Features Demonstrated

### Keystroke Metrics Captured
- **Dwell Time:** How long each key is held down
- **Flight Time:** Time between releasing one key and pressing the next
- **Typing Speed:** Overall words per minute
- **Key Patterns:** Unique rhythm of your typing

### Detection Capabilities
- Identifies normal user typing
- Detects timing anomalies (slow, fast, hesitant typing)
- Catches inconsistent patterns
- Provides confidence scores (0-100%)

### User Experience
- Smooth form validation
- Progress tracking during training
- Real-time test execution
- Comprehensive results display
- Responsive design (works on mobile too)

## Endpoints Used

The frontend communicates with these backend endpoints:

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/register` | Register new user |
| POST | `/train` | Submit training keystrokes |
| POST | `/predict` | Get prediction for test |

## Troubleshooting

### "Connection error" appears

**Problem:** Backend not running or wrong URL
**Solution:** 
```bash
cd backend
python app.py
```
Make sure it's running on port 8000

### "Type exactly: greyc laboratory" error

**Problem:** Text doesn't match exactly
**Solution:** 
- Must be lowercase
- Must include the space between words
- Cannot have typos

### Frontend won't load

**Problem:** Frontend dependencies missing
**Solution:**
```bash
cd frontend
npm install
npm run dev
```

### Browser shows blank page

**Problem:** Port 5173 already in use
**Solution:**
- Kill process using port 5173
- Or use: `PORT=3000 npm run dev`

## File Structure

```
frontend/
├── src/
│   ├── App.jsx                     # Main component with navigation
│   ├── pages/
│   │   ├── Register.jsx            # Registration form
│   │   ├── Capture.jsx             # Training interface
│   │   ├── TestCases.jsx           # Test scenario runner
│   │   └── Dashboard.jsx           # User statistics
│   └── styles/
│       ├── Register.css
│       ├── Capture.css
│       ├── TestCases.css
│       └── Dashboard.css
└── package.json
```

## Commands Reference

```bash
# Install dependencies
npm install

# Start dev server (hot reload)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Stats

- **Total Components:** 5 (App + 4 pages)
- **Total CSS Files:** 5
- **Lines of Code:** ~1000+ (JavaScript) + ~1500+ (CSS)
- **Training Rounds:** 10
- **Test Scenarios:** 5
- **Feature Metrics:** 31 values extracted per keystroke sequence

## What's Happening Behind the Scenes

1. **Frontend captures** keystroke timings (keydown/keyup)
2. **Backend extracts** 31 features from the keystroke data
3. **ML models** (One-Class SVM + Random Forest) make predictions
4. **Frontend displays** results with confidence scores

## Success Indicators

✅ You should see:
- Registration form accepting your profile
- Training progress bar reaching 100%
- "Legitimate User" test showing NORMAL prediction
- "Intruder" tests showing INTRUDER predictions  
- Dashboard showing your stats and test results

## Next Steps

- Customize the test cases
- Export your typing profile
- Integrate with a login system
- Add multi-user support
- Deploy to production

---

**Questions?** Check the FRONTEND_README.md for detailed documentation.
