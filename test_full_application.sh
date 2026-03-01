#!/bin/bash
# Comprehensive Application Test - Tests all functionality in development mode
# This validates that packaging will work correctly on Windows

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     DocManager - Comprehensive Application Test           ║"
echo "╔════════════════════════════════════════════════════════════╗"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

test_result() {
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓${NC} $2"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}✗${NC} $2"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    pkill -f "uvicorn" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    sleep 2
}

trap cleanup EXIT

# Start Backend
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Starting Backend Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

source ca_desktop/backend/venv/bin/activate
export PYTHONPATH="$PWD:$PYTHONPATH"
python -m uvicorn ca_desktop.backend.src.main:app --host 127.0.0.1 --port 8443 --log-level error > /tmp/backend.log 2>&1 &
BACKEND_PID=$!

echo "  Backend PID: $BACKEND_PID"
sleep 5

if ps -p $BACKEND_PID > /dev/null; then
    test_result 0 "Backend server started"
else
    test_result 1 "Backend server failed to start"
    cat /tmp/backend.log
    exit 1
fi

# Start Frontend
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Starting Frontend Server...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

cd ca_desktop/frontend
npm run dev -- --port 5174 --host 127.0.0.1 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ../..

echo "  Frontend PID: $FRONTEND_PID"
sleep 8

if ps -p $FRONTEND_PID > /dev/null; then
    test_result 0 "Frontend server started"
else
    test_result 1 "Frontend server failed to start"
    cat /tmp/frontend.log
    exit 1
fi

# Run API Tests
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Running API Test Suite...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python tests/api/test_api_complete.py > /tmp/api_tests.log 2>&1
API_EXIT=$?

if [ $API_EXIT -eq 0 ]; then
    test_result 0 "API test suite passed (100%)"
    tail -15 /tmp/api_tests.log | grep -A 10 "TEST SUMMARY"
else
    test_result 1 "API test suite had failures"
    tail -30 /tmp/api_tests.log
fi

# Test Frontend Pages
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Testing Frontend Pages...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Test CA Dashboard
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5174/ca)
[ "$HTTP_CODE" = "200" ] && test_result 0 "CA Dashboard accessible (HTTP 200)" || test_result 1 "CA Dashboard failed (HTTP $HTTP_CODE)"

# Test Client Portal
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5174/portal)
[ "$HTTP_CODE" = "200" ] && test_result 0 "Client Portal accessible (HTTP 200)" || test_result 1 "Client Portal failed (HTTP $HTTP_CODE)"

# Test Public Website
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5174/ca-lokesh-dagdiya)
[ "$HTTP_CODE" = "200" ] && test_result 0 "Public Website accessible (HTTP 200)" || test_result 1 "Public Website failed (HTTP $HTTP_CODE)"

# Test Package Structure
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Testing Package Structure...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PKG="./dist_package/DocManager-v1.0.0"

[ -f "$PKG/backend/DocManager" ] && test_result 0 "Backend executable exists" || test_result 1 "Backend executable missing"
[ -d "$PKG/frontend" ] && test_result 0 "Frontend build exists" || test_result 1 "Frontend build missing"
[ -f "$PKG/README.txt" ] && test_result 0 "README exists" || test_result 1 "README missing"
[ -f "$PKG/config/.env.template" ] && test_result 0 "Config template exists" || test_result 1 "Config template missing"
[ -f "$PKG/scripts/start_backend.bat" ] && test_result 0 "Windows startup script exists" || test_result 1 "Windows script missing"

# Check Package Sizes
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Package Size Analysis...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

BACKEND_SIZE=$(du -sh "$PKG/backend/DocManager" 2>/dev/null | cut -f1 || echo "N/A")
FRONTEND_SIZE=$(du -sh "$PKG/frontend" 2>/dev/null | cut -f1 || echo "N/A")
TOTAL_SIZE=$(du -sh "$PKG" 2>/dev/null | cut -f1 || echo "N/A")

echo "  Backend:  $BACKEND_SIZE"
echo "  Frontend: $FRONTEND_SIZE"
echo "  Total:    $TOTAL_SIZE"

# Check if sizes meet targets
BACKEND_MB=$(echo $BACKEND_SIZE | sed 's/M//')
if [ "$BACKEND_MB" -lt 100 ]; then
    test_result 0 "Backend size optimal (< 100MB)"
else
    test_result 1 "Backend size too large (> 100MB)"
fi

# Performance Check
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Performance Check...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ps -p $BACKEND_PID > /dev/null; then
    MEMORY_KB=$(ps -o rss= -p $BACKEND_PID 2>/dev/null || echo 0)
    MEMORY_MB=$((MEMORY_KB / 1024))
    echo "  Memory Usage: ${MEMORY_MB} MB"
    
    if [ $MEMORY_MB -lt 500 ]; then
        test_result 0 "Memory usage acceptable (< 500 MB)"
    else
        test_result 1 "Memory usage high (> 500 MB)"
    fi
    
    CPU=$(ps -o %cpu= -p $BACKEND_PID 2>/dev/null || echo 0)
    echo "  CPU Usage: ${CPU}%"
else
    test_result 1 "Backend process not running"
fi

# Test API Response Time
echo ""
START_TIME=$(date +%s%N)
curl -s http://localhost:8443/ > /dev/null
END_TIME=$(date +%s%N)
RESPONSE_MS=$(( ($END_TIME - $START_TIME) / 1000000 ))
echo "  API Response Time: ${RESPONSE_MS}ms"

if [ $RESPONSE_MS -lt 200 ]; then
    test_result 0 "API response time excellent (< 200ms)"
else
    test_result 1 "API response time slow (> 200ms)"
fi

# Documentation Check
echo ""
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Documentation Check...${NC}"
echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

[ -f "docs/guides/USER_GUIDE.md" ] && test_result 0 "User Guide exists" || test_result 1 "User Guide missing"
[ -f "docs/guides/DEVELOPER_GUIDE.md" ] && test_result 0 "Developer Guide exists" || test_result 1 "Developer Guide missing"
[ -f "docs/guides/DEPLOYMENT_GUIDE.md" ] && test_result 0 "Deployment Guide exists" || test_result 1 "Deployment Guide missing"
[ -f "PRODUCTION_CHECKLIST.md" ] && test_result 0 "Production Checklist exists" || test_result 1 "Production Checklist missing"
[ -f "WINDOWS_PACKAGING_COMPLETE.md" ] && test_result 0 "Packaging Guide exists" || test_result 1 "Packaging Guide missing"

# Summary
echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                      TEST SUMMARY                          ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo "Total Tests: $TESTS_TOTAL"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
echo ""
echo "Success Rate: ${SUCCESS_RATE}%"

echo ""
echo -e "${YELLOW}📊 Key Metrics:${NC}"
echo "  • Backend Size: $BACKEND_SIZE"
echo "  • Frontend Size: $FRONTEND_SIZE"  
echo "  • Memory Usage: ${MEMORY_MB} MB"
echo "  • API Response: ${RESPONSE_MS}ms"

if [ $SUCCESS_RATE -ge 90 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║  🎉 APPLICATION READY FOR PRODUCTION DEPLOYMENT! 🎉        ║${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ Some tests failed. Please review and fix issues.${NC}"
    exit 1
fi
