#!/bin/bash

# Social Signal Tracker - Start Script

echo "🚀 Starting Social Signal Tracker..."
echo ""

# Check if we're in the right directory
if [ ! -d "scraper" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $API_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Create data directory
mkdir -p scraper/data

# Start the API server
echo "📡 Starting API server on http://localhost:8000..."
cd scraper
source venv/bin/activate
uvicorn api:app --host 0.0.0.0 --port 8000 &
API_PID=$!
cd ..

# Wait for API to start
sleep 3

# Start the frontend
echo "🎨 Starting frontend on http://localhost:3000..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Social Signal Tracker is running!"
echo ""
echo "   📊 Dashboard: http://localhost:3000"
echo "   📡 API:       http://localhost:8000"
echo "   📚 API Docs:  http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
