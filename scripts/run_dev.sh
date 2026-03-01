#!/bin/bash

# Function to handle cleanup on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p)
    exit
}

trap cleanup SIGINT SIGTERM

# Get project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Starting CA Desktop Development Environment..."

# 1. Start Backend
echo "📦 Starting Backend (http://localhost:8443)..."
source venv/bin/activate
cd ca_desktop/backend
uvicorn src.main:app --reload --port 8443 --host 0.0.0.0 &
BACKEND_PID=$!

# 2. Start Frontend
echo "💻 Starting Frontend (http://localhost:5173)..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Environment running. Press Ctrl+C to stop."
wait
