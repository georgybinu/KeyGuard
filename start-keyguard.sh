#!/bin/bash

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cleanup() {
  pkill -P $$ || true
  exit 0
}

trap cleanup SIGINT SIGTERM

echo "Starting KeyGuard web app..."

cd "$PROJECT_ROOT/backend"
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate
pip install -q -r requirements.txt >/dev/null 2>&1 || true
uvicorn app:app --reload --host 0.0.0.0 --port 8000 > "$PROJECT_ROOT/backend.log" 2>&1 &

cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
  npm install >/dev/null 2>&1
fi
npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1 &

echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo "Press Ctrl+C to stop both."

wait
