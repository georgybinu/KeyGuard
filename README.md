# KeyGuard - Keystroke-Based Intrusion Detection System

A machine learning system that analyzes keystroke dynamics to detect intrusion attempts.

## 🚀 Quick Start

### Option 1: Demo Mode (No UI - 1 minute)
```bash
python3 demo.py
```
Simulates keystroke capture, feature extraction, and ML predictions.

### Option 2: Full Stack (With UI)
```bash
./start-keyguard.sh
```
Starts backend (port 8000) and frontend (port 5173), opens browser automatically.

### Option 3: Docker
```bash
docker-compose up
```
Runs all services in containers with PostgreSQL.

## 📋 What's Included

- **Frontend**: React + Vite (http://localhost:5173)
- **Backend**: FastAPI with feature extraction (http://localhost:8000)
- **ML Models**: One-Class SVM + Random Forest for anomaly detection
- **Feature Pipeline**: Extracts dwell and flight times from keystrokes

## 📊 How It Works

1. User types "greyc laboratory"
2. Frontend captures keystroke timings
3. Backend extracts 31 features (16 dwell + 15 flight times)
4. ML model predicts: "normal" or "intruder"
5. Result displayed in UI

## 🔌 API Endpoints

- `POST /predict` - Predict intrusion from keystrokes
- `POST /train` - Train user behavior profile
- `POST /capture/start` - Start keystroke session
- `POST /capture/end` - End keystroke session

API Documentation: http://localhost:8000/docs (when running)

## 📁 Project Structure

```
KeyGuard/
├── demo.py                    # Standalone demo script
├── start-keyguard.sh          # Auto-start script
├── docker-compose.yml         # Docker orchestration
│
├── backend/
│   ├── app.py                 # FastAPI main
│   ├── Dockerfile             # Backend container
│   ├── requirements.txt        # Python dependencies
│   ├── routes/                # API endpoints
│   ├── services/              # Feature extraction
│   └── utils/                 # Config & logging
│
├── frontend/
│   ├── Dockerfile             # Frontend container
│   ├── src/                   # React components
│   └── vite.config.js         # Vite config
│
└── ml/
    ├── predict.py             # ML prediction
    ├── models/                # Trained models
    ├── profiles/              # User profiles
    └── feature_engineering/   # Feature code
```

## ✨ Features

- Real-time keystroke analysis
- Dwell time extraction (key hold duration)
- Flight time extraction (gaps between keys)
- User profile training
- One-Class SVM for anomaly detection
- Random Forest for classification
- RESTful API with documentation
- Interactive React UI
- Database persistence
- Docker support

## ⚙️ Requirements

- Python 3.9+
- Node.js 16+
- npm or yarn
- Docker (optional)

## 🐛 Troubleshooting

**Port already in use:**
```bash
lsof -i :8000    # Check port 8000
kill -9 <PID>    # Kill process
```

**Dependencies not installed:**
```bash
cd backend && pip install -r requirements.txt
cd frontend && npm install
```

## 📚 Documentation

- **ML_MODEL_FORMAT_REFERENCE.md** - Feature format and ML model details
- **FRONTEND_BACKEND_INTEGRATION.md** - API integration guide

## 🎯 Example Usage

```python
from ml.predict import predict_anomaly

# 31-value feature vector (16 dwell + 15 flight times)
features = [0.12, 0.10, 0.11, ..., 0.08, 0.07]

# Predict
result = predict_anomaly("username", features)
# Returns: "normal" or "intruder"
```

## 📈 Next Steps

1. Run `python3 demo.py` to see system in action
2. Run `./start-keyguard.sh` for full UI experience
3. Register a user and train your typing pattern
4. Test intrusion detection with different typing styles

---

**Status**: ✅ Ready for Demo  
**Version**: 1.0.0  
**Last Updated**: March 25, 2026