#!/bin/bash

# ╔══════════════════════════════════════════════════════════════╗
# ║     OSINT Phone Intelligence Platform - Complete Starter     ║
# ║     Startet Backend + Frontend automatisch                   ║
# ╚══════════════════════════════════════════════════════════════╝

# Farben
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Finde das Verzeichnis des Skripts
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/osint-platform-backend"
BACKEND_PORT=15000
BACKEND_PID=""

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     OSINT Phone Intelligence Platform - Starter              ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down server...${NC}"
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        wait $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}✓ Server stopped${NC}"
    fi
    exit 0
}

trap cleanup INT TERM

# Check Python
echo -e "${BLUE}[1/4] Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"

# Check Backend Directory
echo -e "${BLUE}[2/4] Checking Backend...${NC}"
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}ERROR: Backend directory not found at $BACKEND_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Backend directory found${NC}"

# Setup Backend
echo -e "${BLUE}[3/4] Configuring Backend...${NC}"
cd "$BACKEND_DIR"

# Create .env if not exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env file...${NC}"
    cat > .env << 'EOF'
FLASK_ENV=production
DEBUG=False
SECRET_KEY=osint-platform-secret-key-2024-change-this
HOST=0.0.0.0
PORT=15000
RATE_LIMIT=1000 per hour
DATABASE_URL=sqlite:///osint.db
CACHE_TYPE=simple
CACHE_TIMEOUT=3600

# AI Service API Keys (Encrypted)
KIMI_API_KEY=ENC:c3Uud24wESVqfwZGXiISbVaih4-TvryQ0vrj44L91-OXl9VbNx4BXwgQcBxlA1RQZFY8BA==
PERPLEXITY_API_KEY=ENC:cG5vd3cmOR50fRkIUiALLUK2osLMu7z5zY3i1vrqyqaImYwbNRsnLw8JfWFMBw1sZ0c9eH4y

DATA_RETENTION_DAYS=7
LOG_LEVEL=INFO
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Install Python dependencies if needed
echo -e "${YELLOW}Checking Python dependencies...${NC}"
python3 -c "import flask, flask_cors, phonenumbers, duckduckgo_search, requests" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${YELLOW}Installing dependencies (this may take a moment)...${NC}"
    pip3 install flask flask-cors flask-limiter flask-talisman phonenumbers duckduckgo-search requests python-dotenv -q
    if [ $? -ne 0 ]; then
        echo -e "${RED}ERROR: Failed to install dependencies${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Dependencies ready${NC}"

# Build Frontend into Backend static folder
echo -e "${BLUE}[4/4] Building Frontend...${NC}"
if [ -d "$SCRIPT_DIR/app" ]; then
    cd "$SCRIPT_DIR/app"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing npm packages...${NC}"
        npm install
    fi
    
    # Create production .env.local (backend serves frontend)
    echo "VITE_API_URL=/api" > .env.local
    
    # Build frontend
    echo -e "${YELLOW}Building frontend...${NC}"
    npm run build 2>&1 | tail -5
    
    # Copy build to backend static folder
    if [ -d "dist" ]; then
        rm -rf "$BACKEND_DIR/static"/* 2>/dev/null
        cp -r dist/* "$BACKEND_DIR/static/"
        echo -e "${GREEN}✓ Frontend built and copied${NC}"
    fi
fi

# Start Backend
echo ""
echo -e "${BLUE}Starting Server...${NC}"
cd "$BACKEND_DIR"

# Kill any existing process on port 15000
echo -e "${YELLOW}Checking for existing processes on port $BACKEND_PORT...${NC}"
lsof -ti:$BACKEND_PORT | xargs kill -9 2>/dev/null
sleep 1

# Start the server
echo -e "${YELLOW}Starting OSINT Platform on port $BACKEND_PORT...${NC}"
python3 app.py &
BACKEND_PID=$!

# Wait for server to be ready
echo -e "${YELLOW}Waiting for server to start...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
        break
    fi
    echo -n "."
    sleep 1
done
echo ""

# Check if server started successfully
if ! curl -s http://localhost:$BACKEND_PORT/api/health > /dev/null 2>&1; then
    echo -e "${RED}ERROR: Server failed to start!${NC}"
    echo -e "${YELLOW}Check the error messages above or run manually:${NC}"
    echo -e "  cd $BACKEND_DIR && python3 app.py"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Get IP addresses
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# Success message
echo ""
echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     ✓ OSINT Platform is RUNNING!                             ║${NC}"
echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}🌐 OPEN YOUR BROWSER:${NC}"
echo -e "   ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo ""
echo -e "${BLUE}📱 Or from another device on your network:${NC}"
echo -e "   ${GREEN}http://$IP_ADDRESS:$BACKEND_PORT${NC}"
echo ""
echo -e "${BLUE}📊 API Health Check:${NC}"
echo -e "   http://localhost:$BACKEND_PORT/api/health"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop the server${NC}"
echo ""

# Keep script running
wait $BACKEND_PID
