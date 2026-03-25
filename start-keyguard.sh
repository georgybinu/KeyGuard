#!/bin/bash
# KeyGuard Full Stack Startup Script
# Starts both backend API and frontend dev server

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

print_header() {
    echo -e "\n${BLUE}╔════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║ $1${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════╝${NC}\n"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check if running on macOS or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    OPEN_CMD="open"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OPEN_CMD="xdg-open"
else
    OPEN_CMD="echo"
fi

print_header "KeyGuard Full Stack Startup"

# Function to cleanup on exit
cleanup() {
    print_info "Shutting down KeyGuard services..."
    pkill -P $$ || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
print_info "Starting Backend (FastAPI) on port 8000..."
cd "$PROJECT_ROOT/backend"

# Check if Python venv exists, if not create it
if [ ! -d "venv" ]; then
    print_info "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate

# Install requirements
if [ -f "requirements.txt" ]; then
    print_info "Installing Python dependencies..."
    pip install -q -r requirements.txt 2>/dev/null || true
fi

# Start backend in background
python app.py > "$PROJECT_ROOT/backend.log" 2>&1 &
BACKEND_PID=$!
print_success "Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
print_info "Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "Backend is ready!"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start. Check backend.log for details."
        cat "$PROJECT_ROOT/backend.log"
        exit 1
    fi
    sleep 1
done

# Start Frontend
print_info "Starting Frontend (React + Vite) on port 5173..."
cd "$PROJECT_ROOT/frontend"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_info "Installing Node dependencies..."
    npm install -q 2>/dev/null || npm install
fi

# Start frontend in background
npm run dev > "$PROJECT_ROOT/frontend.log" 2>&1 &
FRONTEND_PID=$!
print_success "Frontend started (PID: $FRONTEND_PID)"

# Wait for frontend to start
print_info "Waiting for frontend to be ready..."
sleep 5

# Display startup information
print_header "KeyGuard is Running!"

cat << EOF
${GREEN}Backend API:${NC}
  URL: http://localhost:8000
  Docs: http://localhost:8000/docs
  Health: http://localhost:8000/health

${GREEN}Frontend:${NC}
  URL: http://localhost:5173
  
${YELLOW}Getting Started:${NC}
  1. Open http://localhost:5173 in your browser
  2. Register a new account
  3. Complete keystroke training (type "greyc laboratory" ~10 times)
  4. Test the intrusion detection system
  
${YELLOW}Logs:${NC}
  Backend:  $PROJECT_ROOT/backend.log
  Frontend: $PROJECT_ROOT/frontend.log
  
${YELLOW}To stop:${NC}
  Press Ctrl+C

EOF

# Try to open browser (macOS/Linux)
if command -v $OPEN_CMD &> /dev/null; then
    print_info "Opening browser to http://localhost:5173..."
    sleep 2
    $OPEN_CMD "http://localhost:5173" 2>/dev/null || true
fi

# Keep script running
print_info "KeyGuard is running. Press Ctrl+C to stop."
wait
