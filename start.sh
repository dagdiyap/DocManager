#!/bin/bash

# DocManager CA Desktop - Local Development Startup Script
# This script starts both backend and frontend servers

set -e

echo "🚀 Starting DocManager CA Desktop..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if backend directory exists
if [ ! -d "ca_desktop/backend" ]; then
    echo "❌ Error: ca_desktop/backend directory not found"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "ca_desktop/frontend" ]; then
    echo "❌ Error: ca_desktop/frontend directory not found"
    exit 1
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill 0
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo -e "${BLUE}📦 Starting Backend Server...${NC}"
cd ca_desktop/backend
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    source venv/bin/activate
    echo -e "${YELLOW}⚠️  Upgrading pip, setuptools, and wheel...${NC}"
    pip install --upgrade pip setuptools wheel
    echo -e "${YELLOW}⚠️  Installing dependencies...${NC}"
    pip install -r requirements.txt
else
    source venv/bin/activate
    # Ensure pip, setuptools, and wheel are up to date
    pip install --upgrade pip setuptools wheel --quiet
fi

# Check if database exists in project root, if not create it
if [ ! -f "../../ca_desktop.db" ]; then
    echo -e "${YELLOW}⚠️  Database not found. Running setup...${NC}"
    cd ../..
    source ca_desktop/backend/venv/bin/activate
    python scripts/setup_database.py
    cd ca_desktop/backend
fi

# Install shared module if not already installed
pip list | grep ca-shared > /dev/null || pip install --no-deps -e ../../shared

# Set PYTHONPATH to include project root (cross-platform, not hardcoded)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PYTHONPATH="${SCRIPT_DIR}:$PYTHONPATH"

uvicorn ca_desktop.backend.src.main:app --host 127.0.0.1 --port 8443 --reload &
BACKEND_PID=$!
cd ../..

echo -e "${GREEN}✅ Backend started on http://localhost:8443${NC}"
echo ""

# Wait a bit for backend to start
sleep 3

# Start Frontend
echo -e "${BLUE}🎨 Starting Frontend Server...${NC}"
cd ca_desktop/frontend

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}⚠️  Node modules not found. Installing...${NC}"
    npm install
fi

npm run dev &
FRONTEND_PID=$!
cd ../..

echo -e "${GREEN}✅ Frontend started on http://localhost:5174${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 DocManager CA Desktop is running!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 Access Points:"
echo "   • CA Login:        http://localhost:5174/ca/login"
echo "   • Client Portal:   http://localhost:5174/portal/login"
echo "   • Public Website:  http://localhost:5174/ca-lokesh-dagdiya"
echo "   • API Docs:        http://localhost:8443/docs"
echo ""
echo "🔑 Demo Credentials:"
echo "   CA Admin:  lokesh / lokesh"
echo "   Client:    9876543210 / client123"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait
