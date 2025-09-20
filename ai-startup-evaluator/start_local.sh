#!/bin/bash

# AI Startup Evaluator - Local Development Startup Script

echo "🚀 Starting AI Startup Evaluator (Local Development)"
echo "=================================================="

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the ai-startup-evaluator directory"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $1 is already in use"
        return 1
    else
        return 0
    fi
}

# Check required ports
echo "🔍 Checking ports..."
if ! check_port 8000; then
    echo "   Backend port 8000 is busy. Please stop the existing process."
    exit 1
fi

if ! check_port 3000; then
    echo "   Frontend port 3000 is busy. Please stop the existing process."
    exit 1
fi

echo "✅ Ports 8000 and 3000 are available"

# Check if setup has been run
if [ ! -f "backend/startup_evaluator.db" ]; then
    echo "⚠️  Database not found. Running setup first..."
    python setup_local.py
fi

# Check for Google AI API key
if ! grep -q "GOOGLE_AI_API_KEY=.*[^#]" backend/.env 2>/dev/null; then
    echo ""
    echo "⚠️  Google AI API Key not configured!"
    echo "   1. Get an API key from: https://aistudio.google.com/"
    echo "   2. Add it to backend/.env: GOOGLE_AI_API_KEY=your-key-here"
    echo "   3. The app will work with limited functionality without it"
    echo ""
fi

# Start backend in background
echo "🔧 Starting Backend (FastAPI)..."
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# Wait a moment for backend to start
sleep 3

# Check if backend started successfully
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "❌ Backend failed to start. Check the logs above."
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "✅ Backend started successfully at http://localhost:8000"

# Start frontend in background
echo "🎨 Starting Frontend (React)..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Frontend starting at http://localhost:3000"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

echo ""
echo "🎉 AI Startup Evaluator is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for processes
wait
