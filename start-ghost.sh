#!/bin/bash

# ===========================================
# Ghost Production Startup Script
# ===========================================

set -e

echo ""
echo "🔮 GHOST - Predictive Intelligence Platform"
echo "==========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")"

# Check environment file
if [ ! -f scraper/.env ]; then
    echo -e "${RED}✗ scraper/.env not found${NC}"
    echo "  Run: cp scraper/.env.example scraper/.env"
    echo "  Then add your API keys"
    exit 1
fi

# Load environment
export $(cat scraper/.env | grep -v '^#' | grep -v '^$' | xargs)

echo "Checking API keys..."
echo ""

check_key() {
    if [ -z "${!1}" ] || [ "${!1}" = "..." ] || [[ "${!1}" == *"..."* ]]; then
        echo -e "  ${YELLOW}○${NC} $1 - not configured"
        return 1
    else
        echo -e "  ${GREEN}●${NC} $1 - configured"
        return 0
    fi
}

echo "Required:"
check_key ANTHROPIC_API_KEY || true
check_key YOUTUBE_API_KEY || true
check_key NEWSAPI_KEY || true

echo ""
echo "Recommended:"
check_key POLYGON_API_KEY || true
check_key QUIVER_API_KEY || true

echo ""

# Create data directory
mkdir -p scraper/data

# Cleanup function
cleanup() {
    echo ""
    echo "Shutting down Ghost..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start backend
echo "Starting backend API..."
cd scraper

if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate

# Install/update dependencies
pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt

# Start API server
python -m uvicorn api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait for backend
sleep 3

# Check backend health
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Backend running${NC}"
else
    echo -e "${YELLOW}! Backend may still be starting...${NC}"
fi

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

sleep 3

echo ""
echo "==========================================="
echo -e "${GREEN}🔮 Ghost is running!${NC}"
echo "==========================================="
echo ""
echo -e "  ${BLUE}Frontend:${NC}  http://localhost:3000"
echo -e "  ${BLUE}Backend:${NC}   http://localhost:8000"
echo -e "  ${BLUE}API Docs:${NC}  http://localhost:8000/docs"
echo ""
echo "Quick commands:"
echo "  curl -X POST http://localhost:8000/api/fetch  # Fetch all sources"
echo "  curl http://localhost:8000/api/stats          # Check data stats"
echo "  curl http://localhost:8000/api/signals        # Get signals"
echo ""
echo "Press Ctrl+C to stop"
echo ""

wait
