# KeyGuard Frontend - Visual Demo Guide

## 🎨 Complete User Journey

```
┌─────────────────────────────────────────────────────────────────┐
│                    KEYGUARD DEMO FLOW                           │
└─────────────────────────────────────────────────────────────────┘

START
  │
  ├─→ Page 1: REGISTRATION PAGE
  │   ├─ Fields: Username, Email, Phone, Password
  │   ├─ Button: "Create Profile"
  │   └─ Info: Shows KeyGuard features & capabilities
  │
  ├─→ Page 2: KEYSTROKE TRAINING (Capture)
  │   ├─ Phase 1 (Ready State)
  │   │  └─ Button: "Start Training Session"
  │   │
  │   ├─ Phase 2 (Training State - 10 Rounds)
  │   │  ├─ Round Counter: 1/10 → 2/10 → ... → 10/10
  │   │  ├─ Required Text: "greyc laboratory"
  │   │  ├─ Progress Bar: 0% → 100% per round
  │   │  ├─ Keystrokes Collected: Shows count
  │   │  └─ Button: "Submit Round" (enabled when text matches)
  │   │
  │   └─ Phase 3 (Completed State)
  │      ├─ Success Icon: ✅
  │      ├─ Statistics: Rounds, Keystrokes, Profile Status
  │      └─ Message: "Training Complete!"
  │
  ├─→ Navigation: "Training" tab in header
  │   
  ├─→ Page 3: TEST CASES
  │   ├─ View 1: Test Selection Grid (5 cards)
  │   │  ├─ Card 1: Legitimate User (Normal)
  │   │  │  └─ Color: Green
  │   │  ├─ Card 2: Slow Intruder
  │   │  │  └─ Color: Red
  │   │  ├─ Card 3: Fast Intruder
  │   │  │  └─ Color: Red
  │   │  ├─ Card 4: Hesitant Intruder
  │   │  │  └─ Color: Red
  │   │  └─ Card 5: Inconsistent Intruder
  │   │     └─ Color: Red
  │   │
  │   ├─ View 2: Test Execution (Per Test)
  │   │  ├─ Test Description: "Type with [specific pattern]"
  │   │  ├─ Input: Text area to type phrase
  │   │  ├─ Progress: Keystroke count
  │   │  └─ Button: "Run Test"
  │   │
  │   └─ View 3: Test Results
  │      ├─ Title: Test name
  │      ├─ Status Badge: ✅ PASSED or ❌ FAILED
  │      ├─ Prediction: "NORMAL" or "INTRUDER"
  │      ├─ Confidence Scores:
  │      │  ├─ RF Model: XX%
  │      │  ├─ SVM Model: XX%
  │      │  └─ Overall: XX%
  │      ├─ Features Display:
  │      │  ├─ Dwell Time: 0.12 sec
  │      │  ├─ Flight Time: 0.08 sec
  │      │  ├─ Typing Speed: 75 WPM
  │      │  └─ Keystroke Count: 160
  │      └─ Buttons: "Back" | "Run Another Test"
  │
  ├─→ Navigation: "Test Cases" tab in header (after training)
  │   
  ├─→ Page 4: DASHBOARD
  │   ├─ Section 1: Header
  │   │  ├─ Title: "👤 [Username]'s Profile"
  │   │  └─ Button: "Logout"
  │   │
  │   ├─ Section 2: Stats Grid (4 cards)
  │   │  ├─ Card 1: Total Tests (count)
  │   │  ├─ Card 2: Success Rate (percentage)
  │   │  ├─ Card 3: Accuracy (percentage)
  │   │  └─ Card 4: Training Status (Trained & Ready)
  │   │
  │   ├─ Section 3: User Profile
  │   │  ├─ Item: Username
  │   │  ├─ Item: Email
  │   │  ├─ Item: Phone
  │   │  └─ Item: Registration Date
  │   │
  │   ├─ Section 4: Training Status
  │   │  ├─ Rounds Completed: 10/10 (progress bar)
  │   │  ├─ Profile Status: Trained & Ready (badge)
  │   │  └─ Training Date: [date]
  │   │
  │   ├─ Section 5: Feature Profile (Grid)
  │   │  ├─ Card: Avg Dwell Time (0.12 sec)
  │   │  ├─ Card: Avg Flight Time (0.08 sec)
  │   │  ├─ Card: Typing Speed (75 WPM)
  │   │  └─ Card: Keystroke Count (160)
  │   │
  │   ├─ Section 6: Detection Statistics
  │   │  ├─ Total Detections: X
  │   │  ├─ Normal Attempts: X
  │   │  ├─ Intruders Detected: X
  │   │  └─ Accuracy: XX%
  │   │
  │   ├─ Section 7: Activity Log
  │   │  ├─ Entry: "Legitimate User Test - PASSED - 10:30 AM"
  │   │  ├─ Entry: "Slow Intruder Test - PASSED - 10:28 AM"
  │   │  └─ ... (recent activities)
  │   │
  │   └─ Section 8: System Info Boxes
  │      ├─ "How Detection Works"
  │      ├─ "Keystroke Metrics"
  │      └─ "Profile Security"
  │
  ├─→ Navigation: "Dashboard" tab in header (after training)
  │   
  └─→ Logout: Return to Registration Page

```

## 📐 Page Layouts

### Page 1: Registration

```
╔═══════════════════════════════════════════════════╗
║              🔐 KeyGuard Registration            ║
║           Create your biometric typing profile    ║
╠═══════════════════════════════════════════════════╣
║                                                   ║
║  ┌─ Username ───────────────────────────────────┐ ║
║  │ [                                           ] │ ║
║  └───────────────────────────────────────────────┘ ║
║                                                   ║
║  ┌─ Email ───────────────────────────────────────┐ ║
║  │ [                                           ] │ ║
║  └───────────────────────────────────────────────┘ ║
║                                                   ║
║  ┌─ Phone ───────────────────────────────────────┐ ║
║  │ [                                           ] │ ║
║  └───────────────────────────────────────────────┘ ║
║                                                   ║
║  ┌─ Password ────────────────────────────────────┐ ║
║  │ [                                           ] │ ║
║  └───────────────────────────────────────────────┘ ║
║                                                   ║
║          ┌─ CREATE PROFILE ────────────────────┐  ║
║          │   (Gradient Purple Button)          │  ║
║          └────────────────────────────────────┘  ║
║                                                   ║
║  ┌─ What is KeyGuard? ───────────────────────────┐ ║
║  │ • Keystroke biometric authentication          │ ║
║  │ • Unique typing pattern recognition           │ ║
║  │ • Machine learning-based detection            │ ║
║  └───────────────────────────────────────────────┘ ║
║                                                   ║
╚═══════════════════════════════════════════════════╝
```

### Page 2: Training

```
╔═══════════════════════════════════════════════════════════════╗
║                    📝 Keystroke Training                      ║
║          Typing | Test Cases | Dashboard | Logout             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  READY STATE                                                  ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ Welcome to KeyGuard Training                             │ ║
║  │ You will type "greyc laboratory" 10 times               │ ║
║  │ This creates your unique biometric typing profile        │ ║
║  │                                                          │ ║
║  │ What we measure:                                         │ ║
║  │ • Dwell Time: How long you hold each key               │ ║
║  │ • Flight Time: Gap between releasing & pressing         │ ║
║  │ • Typing Speed: Your overall typing rhythm              │ ║
║  │ • Key Intervals: Time patterns between keystrokes       │ ║
║  │                                                          │ ║
║  │  ┌─ START TRAINING SESSION ────────────────────┐        │ ║
║  │  │  (Gradient Purple Button)                    │        │ ║
║  │  └─────────────────────────────────────────────┘        │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  TRAINING STATE (Repeat 10 times)                             ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ Round 3 of 10                                    30%      │ ║
║  │ ███████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │ ║
║  │                                                          │ ║
║  │  Type:  greyc laboratory                               │ ║
║  │                                                          │ ║
║  │  ┌────────────────────────────────────────────────────┐ ║
║  │  │ [Your typing goes here as you type...]              │ ║
║  │  │                                                    │ ║
║  │  │                                                    │ ║
║  │  └────────────────────────────────────────────────────┘ ║
║  │                                                          │ ║
║  │  Status: ✓ Text matches! (156 keystrokes)              │ ║
║  │                                                          │ ║
║  │  ┌─ SUBMIT ROUND ──┐                                    │ ║
║  │  │ (Green Button)  │                                    │ ║
║  │  └─────────────────┘                                    │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  COMPLETED STATE                                              ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │                         🎉                               │ ║
║  │                 Training Complete!                       │ ║
║  │                                                          │ ║
║  │  Training Statistics:                                    │ ║
║  │  • Rounds Completed: 10                                 │ ║
║  │  • Total Keystrokes: 1,560                              │ ║
║  │  • Phrase: "greyc laboratory"                           │ ║
║  │  • Status: Profile Created ✓                            │ ║
║  │                                                          │ ║
║  │  Your profile is now ready.                             │ ║
║  │  Go to Test Cases to verify detection.                  │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Page 3: Test Cases

```
╔═══════════════════════════════════════════════════════════════╗
║                    🛡️ Test Cases                              ║
║          Typing | Test Cases | Dashboard | Logout             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  TEST SELECTION VIEW                                          ║
║  ┌───────────────────┐  ┌───────────────────┐  ┌───────────┐ ║
║  │ Legitimate User   │  │ Slow Intruder     │  │ Fast      │ ║
║  │ (Normal Typing)   │  │ (Slow deliberate) │  │ Intruder  │ ║
║  │ Expected:         │  │ Expected:         │  │ Expected: │ ║
║  │ NORMAL ✅          │  │ INTRUDER 🚨        │  │ INTRUDER  │ ║
║  └───────────────────┘  └───────────────────┘  └───────────┘ ║
║  ┌───────────────────┐  ┌───────────────────┐                ║
║  │ Hesitant          │  │ Inconsistent      │                ║
║  │ Intruder          │  │ Intruder          │                ║
║  │ (Long pauses)     │  │ (Variable speed)  │                ║
║  │ Expected:         │  │ Expected:         │                ║
║  │ INTRUDER 🚨        │  │ INTRUDER 🚨        │                ║
║  └───────────────────┘  └───────────────────┘                ║
║                                                               ║
║  TEST EXECUTION VIEW                                          ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ Legitimate User (Normal Typing)        ┌─ BACK ────────┐ │ ║
║  │ Simulate the actual user typing        │ (Gray Button) │ │ ║
║  │ naturally - should result in NORMAL    └───────────────┘ │ ║
║  │                                                          │ ║
║  │  Type:  greyc laboratory                               │ ║
║  │  ┌────────────────────────────────────────────────────┐ │ ║
║  │  │ [Your typing goes here...]                         │ │ ║
║  │  │                                                    │ │ ║
║  │  └────────────────────────────────────────────────────┘ │ ║
║  │                                                          │ ║
║  │  Keystrokes: 156 | Buffer: 5                            │ ║
║  │                                                          │ ║
║  │  ┌──────────────┐  ┌──────────────┐                     │ ║
║  │  │ RUN TEST     │  │ CLEAR        │                     │ ║
║  │  │ (Purple Btn) │  │ (Gray Btn)   │                     │ ║
║  │  └──────────────┘  └──────────────┘                     │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  RESULTS VIEW                                                 ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ 🔍 Detection Result                     ✅ PASSED         │ ║
║  │                                                          │ ║
║  │ Prediction: NORMAL                                      │ ║
║  │ Expected:   NORMAL                                      │ ║
║  │                                                          │ ║
║  │ Confidence Scores:                                      │ ║
║  │ • RF Model: 94.2%                                       │ ║
║  │ • SVM Model: 89.7%                                      │ ║
║  │ • Overall: 92.0%                                        │ ║
║  │                                                          │ ║
║  │ Feature Analysis:                                       │ ║
║  │ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │ ║
║  │ │Dwell Time│ │Flight Tim│ │Typing Sp │ │Keystroke │    │ ║
║  │ │  0.12 s  │ │  0.08 s  │ │ 75 WPM  │ │ Count: 160    │ ║
║  │ └──────────┘ └──────────┘ └──────────┘ └──────────┘    │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### Page 4: Dashboard

```
╔═══════════════════════════════════════════════════════════════╗
║                    📊 Dashboard                               ║
║          Typing | Test Cases | Dashboard | Logout             ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  STATS GRID (4 Cards)                                         ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        ║
║  │ Total Tests  │  │ Successful   │  │ Detection    │        ║
║  │     5        │  │    4         │  │ Accuracy 80% │        ║
║  └──────────────┘  └──────────────┘  └──────────────┘        ║
║                                                               ║
║  USER PROFILE SECTION                                         ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ Username:         john_doe                               │ ║
║  │ Email:            john@example.com                       │ ║
║  │ Phone:            123-456-7890                           │ ║
║  │ Registration:     Dec 15, 2024                           │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  TRAINING STATUS                                              ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ Rounds Completed:           10/10  [████████████] 100% │ ║
║  │ Profile Status:             ✓ Trained & Ready          │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  FEATURE PROFILE (Grid)                                       ║
║  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        ║
║  │ Avg Dwell    │  │ Avg Flight   │  │ Typing Speed │        ║
║  │ Time: 0.12s  │  │ Time: 0.08s  │  │ 75 WPM       │        ║
║  └──────────────┘  └──────────────┘  └──────────────┘        ║
║                                                               ║
║  ACTIVITY LOG                                                 ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ Legitimate User Test        PASSED    10:30 AM           │ ║
║  │ Slow Intruder Test          PASSED    10:28 AM           │ ║
║  │ Fast Intruder Test          PASSED    10:26 AM           │ ║
║  │ Hesitant Intruder Test      PASSED    10:24 AM           │ ║
║  │ Inconsistent Intruder Test  PASSED    10:22 AM           │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
║  SYSTEM INFORMATION                                           ║
║  ┌──────────────────────────────────────────────────────────┐ ║
║  │ How Detection Works                                     │ ║
║  │ → Keystroke timing is captured in real-time             │ ║
║  │ → Features extracted: dwell & flight times              │ ║
║  │ → ML models analyze patterns against baseline           │ ║
║  │ → Decision: NORMAL user or INTRUDER                     │ ║
║  └──────────────────────────────────────────────────────────┘ ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## 🎯 Key Metrics Displayed

### Per Keystroke
- **Dwell Time:** How long a key is held (milliseconds)
- **Flight Time:** Gap between key release and next key press (milliseconds)

### Per Session
- **Typing Speed:** Words per minute (WPM)
- **Keystroke Count:** Total number of keystrokes
- **Pattern Score:** Consistency of typing pattern

### Detection Confidence
- **RF Model Confidence:** Random Forest probability (0-100%)
- **SVM Anomaly Score:** One-Class SVM score (0-100%)
- **Overall Confidence:** Combined confidence (0-100%)

## 🎨 Color Coding

| Element | Color | Usage |
|---------|-------|-------|
| Legitimate | 🟢 Green | Normal user prediction |
| Intruder | 🔴 Red | Intrusion detected |
| Primary | 🟣 Purple | Main buttons & headers |
| Success | ✅ Green | Test passed |
| Warning | 🟡 Yellow | Need attention |
| Error | 🚨 Red | Failed tests |

## 📱 Responsive Breakpoints

- **Desktop:** 1200px+ (Full layout)
- **Tablet:** 768px-1199px (Adjusted grid)
- **Mobile:** <768px (Single column)

---

**This frontend provides a complete, visually appealing interface for demonstrating the KeyGuard keystroke authentication system!**
