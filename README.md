# KeyGuard

KeyGuard is a web-based keystroke dynamics authentication mini-project.

It lets a user:
- sign up or log in
- complete training with phrases and paragraphs
- get redirected to a monitored notepad
- receive intrusion alerts when live typing behavior deviates strongly from the trained profile

## Project Structure

```text
KeyGuard/
├── backend/      FastAPI backend, database, ML logic
├── frontend/     React frontend
├── ml/           Training scripts and dataset files
├── start-keyguard.sh
└── train_models.py
```

## Main Flow

1. Open the web app
2. Sign up or log in
3. Complete phrase training
4. Complete paragraph training
5. Get redirected to the notepad
6. Type normally while KeyGuard monitors the typing pattern

## Run The Project

Open two terminals.

### Terminal 1: Backend

```bash
cd /Users/georgy/Documents/College/miniproject/KeyGuard/backend
./venv/bin/pip install -r requirements.txt
./venv/bin/uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend

```bash
cd /Users/georgy/Documents/College/miniproject/KeyGuard/frontend
npm install
npm run dev
```

Then open:

```text
http://localhost:5173
```

## Retrain Offline Models

If you want to rebuild the saved offline models:

```bash
cd /Users/georgy/Documents/College/miniproject/KeyGuard
python3 train_models.py
```

## Notes

- The active app is web-based only.
- The main database used by the backend is `backend/keyguard.db`.
- The saved backend models are in `backend/models/`.
