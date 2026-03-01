#!/bin/bash

# CA Document Manager - Local Orchestration Script
# This script starts all services for local E2E testing.

# Colors for logging
CYAN='\033[0;36m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${CYAN}Starting CA Document Manager Ecosystem (No Docker)...${NC}"

# Ensure Homebrew bin is in PATH for npm/node
export PATH=$PATH:/opt/homebrew/bin

# 1. Activate Virtual Environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Virtual environment 'venv' not found. Please create it first."
    exit 1
fi

# 2. License Server (Backend: 8000)
echo -e "${GREEN}[Backend] Starting License Server on port 8000...${NC}"
python3 -m uvicorn license_server.src.main:app --host 0.0.0.0 --port 8000 --reload &
LICENSE_PID=$!

# 3. CA Desktop (Backend: 8443)
echo -e "${GREEN}[Backend] Starting CA Desktop Backend on port 8443...${NC}"
python3 -m uvicorn ca_desktop.backend.src.main:app --host 0.0.0.0 --port 8443 --reload &
CA_BACKEND_PID=$!

# 4. License Server Admin UI (Frontend: 5173)
echo -e "${BLUE}[Frontend] Starting License Admin UI on port 5173...${NC}"
cd license_server/ui && npm run dev &
LICENSE_UI_PID=$!
cd ../..

# 5. CA Desktop UI (Frontend: 5174)
echo -e "${PURPLE}[Frontend] Starting CA Desktop UI on port 5174...${NC}"
cd ca_desktop/frontend && npm run dev &
CA_UI_PID=$!
cd ../..

echo -e "${CYAN}--------------------------------------------------${NC}"
echo -e "${GREEN}All services are starting up!${NC}"
echo -e "License Admin:  http://localhost:5173"
echo -e "CA Desktop:     http://localhost:5174"
echo -e "License API:    http://localhost:8000/api/v1"
echo -e "CA API:         http://localhost:8443/api/v1"
echo -e "${CYAN}--------------------------------------------------${NC}"
echo "Press Ctrl+C to stop all services."

# Cleanup on exit
trap "kill $LICENSE_PID $CA_BACKEND_PID $LICENSE_UI_PID $CA_UI_PID; echo -e '\n${CYAN}All services stopped.${NC}'; exit" INT

wait
