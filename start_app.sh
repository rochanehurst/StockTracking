#!/bin/bash

# StockTracking App Startup Script
echo "🚀 Starting StockTracking Application..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "   Please create a .env file with your Alpha Vantage API key"
    echo "   Example: ALPHA_VANTAGE_API_KEY=your_api_key_here"
    exit 1
fi

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f "python3 run.py" 2>/dev/null
pkill -f "http.server" 2>/dev/null

# Start Flask backend
echo "🔧 Starting Flask backend on port 5001..."
python3 run.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "📱 Starting frontend server on port 8080..."
cd frontend && python3 -m http.server 8080 &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 2

echo ""
echo "✅ StockTracking App is now running!"
echo ""
echo "📱 Frontend: http://localhost:8080"
echo "🔧 Backend API: http://localhost:5001"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    pkill -f "python3 run.py" 2>/dev/null
    pkill -f "http.server" 2>/dev/null
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait

