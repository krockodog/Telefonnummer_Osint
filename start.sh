#!/bin/bash

# ╔══════════════════════════════════════════════════════════════╗
# ║     OSINT Phone Intelligence Platform - Startup Script       ║
# ║                                                              ║
# ║  This script starts both the backend and frontend servers    ║
# ╚══════════════════════════════════════════════════════════════╝

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
BACKEND_PORT=5000
FRONTEND_PORT=5173

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     OSINT Phone Intelligence Platform - Startup              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to kill process on port
kill_port() {
    local port=$1
    if check_port $port; then
        echo -e "${YELLOW}Port $port is in use. Stopping existing process...${NC}"
        lsof -Pi :$port -sTCP:LISTEN -t | xargs kill -9 2>/dev/null
        sleep 1
    fi
}

# Check Python installation
echo -e "${BLUE}[1/5] Checking Python installation...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed.${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"

# Check Node.js installation
echo -e "${BLUE}[2/5] Checking Node.js installation...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}ERROR: Node.js is not installed.${NC}"
    exit 1
fi
NODE_VERSION=$(node --version)
echo -e "${GREEN}✓ Node.js $NODE_VERSION found${NC}"

# Setup Backend
echo -e "${BLUE}[3/5] Setting up backend...${NC}"
cd osint-platform-backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -q -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}ERROR: Failed to install Python dependencies.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend dependencies installed${NC}"

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Please edit .env file with your configuration${NC}"
fi

# Kill existing backend process
kill_port $BACKEND_PORT

# Start backend in background
echo -e "${GREEN}✓ Starting backend server on port $BACKEND_PORT...${NC}"
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Check if backend is running
if ! check_port $BACKEND_PORT; then
    echo -e "${RED}ERROR: Backend failed to start${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend is running (PID: $BACKEND_PID)${NC}"

# Setup Frontend
echo -e "${BLUE}[4/5] Setting up frontend...${NC}"
cd app

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
    npm install
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install Node.js dependencies.${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Frontend dependencies installed${NC}"

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
    echo -e "${YELLOW}Creating .env.local file...${NC}"
    cp .env.example .env.local
fi

# Kill existing frontend process
kill_port $FRONTEND_PORT

# Start frontend in background
echo -e "${GREEN}✓ Starting frontend development server on port $FRONTEND_PORT...${NC}"
npm run dev &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 5

# Check if frontend is running
if ! check_port $FRONTEND_PORT; then
    echo -e "${RED}ERROR: Frontend failed to start${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Frontend is running (PID: $FRONTEND_PID)${NC}"

# Display status
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     OSINT Phone Intelligence Platform is running!            ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Backend API:${NC}  http://localhost:$BACKEND_PORT"
echo -e "${BLUE}Frontend:${NC}     http://localhost:$FRONTEND_PORT"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo -e "${BLUE}Shutting down servers...${NC}"
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✓ Servers stopped${NC}"
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM

# Keep script running
wait
