#!/bin/bash

# KeyGuard Complete Demo Launcher
# This script starts both backend and frontend for a complete local demo

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   🔐 KeyGuard - Complete Demo Launcher${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if running from correct directory
if [ ! -f "README.md" ]; then
    echo -e "${RED}❌ Error: Please run from the KeyGuard root directory${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
    return $?
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Shutting down...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    echo -e "${GREEN}✓ All processes stopped${NC}"
}

trap cleanup EXIT

echo -e "${YELLOW}Starting KeyGuard Demo...${NC}"
echo ""

# Check backend port
if check_port 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check frontend port
if check_port 5173; then
    echo -e "${YELLOW}⚠️  Port 5173 is already in use${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo -e "${BLUE}Starting Backend...${NC}"
echo -e "${YELLOW}📍 Backend URL: http://localhost:8000${NC}"

# Start backend in background
cd backend
python app.py &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Backend failed to start${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo ""

# Go back to root
cd ..

# Check if frontend directory exists
if [ ! -d "frontend" ]; then
    echo -e "${RED}❌ frontend directory not found${NC}"
    exit 1
fi

echo -e "${BLUE}Starting Frontend...${NC}"
echo -e "${YELLOW}📍 Frontend URL: http://localhost:5173${NC}"
echo ""

# Start frontend in background
cd frontend
npm run dev &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 5

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   ✓ KeyGuard is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${BLUE}📊 Frontend (React):${NC}"
echo -e "   URL: ${YELLOW}http://localhost:5173${NC}"
echo ""
echo -e "${BLUE}🔧 Backend (FastAPI):${NC}"
echo -e "   URL: ${YELLOW}http://localhost:8000${NC}"
echo -e "   API Docs: ${YELLOW}http://localhost:8000/docs${NC}"
echo ""
echo -e "${BLUE}🎯 Demo Flow:${NC}"
echo "   1. Register a new user"
echo "   2. Complete keystroke training (10 rounds of 'greyc laboratory')"
echo "   3. Run test cases to see detection in action"
echo "   4. View results in dashboard"
echo ""
echo -e "${BLUE}📝 To stop the demo:${NC}"
echo "   Press Ctrl+C"
echo ""
echo -e "${YELLOW}Opening browser...${NC}"

# Try to open browser
if command -v open &> /dev/null; then
    open http://localhost:5173
elif command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173
elif command -v start &> /dev/null; then
    start http://localhost:5173
else
    echo -e "${YELLOW}Please open http://localhost:5173 in your browser${NC}"
fi

echo ""
echo -e "${YELLOW}Demo is running. Press Ctrl+C to stop.${NC}"

# Wait for processes
wait
