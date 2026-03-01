#!/bin/bash
# Comprehensive test script for packaged DocManager application

set -e

BACKEND_EXE="./dist_package/DocManager-v1.0.0/backend/DocManager"
BACKEND_URL="http://localhost:8443"
FRONTEND_URL="http://localhost:5174"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║   DocManager Packaged Application - Comprehensive Test    ║"
echo "╔════════════════════════════════════════════════════════════╗"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to print test result
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

# Function to wait for service
wait_for_service() {
    local url=$1
    local max_wait=30
    local waited=0
    
    while [ $waited -lt $max_wait ]; do
        if curl -s "$url" > /dev/null 2>&1; then
            return 0
        fi
        sleep 1
        waited=$((waited + 1))
    done
    return 1
}

# Clean up function
cleanup() {
    echo ""
    echo "🧹 Cleaning up..."
    pkill -f "DocManager" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    sleep 2
}

trap cleanup EXIT

# ============================================================================
# TEST 1: Backend Executable Exists and is Executable
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 1: Backend Executable${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -f "$BACKEND_EXE" ] && [ -x "$BACKEND_EXE" ]; then
    test_result 0 "Backend executable exists and is executable"
    SIZE=$(du -sh "$BACKEND_EXE" | cut -f1)
    echo "  Size: $SIZE"
else
    test_result 1 "Backend executable not found or not executable"
    exit 1
fi

# ============================================================================
# TEST 2: Start Backend Server
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 2: Backend Server Startup${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

echo "Starting backend server..."
$BACKEND_EXE > /tmp/docmanager_test.log 2>&1 &
BACKEND_PID=$!
echo "  PID: $BACKEND_PID"

if wait_for_service "$BACKEND_URL"; then
    test_result 0 "Backend server started successfully"
else
    test_result 1 "Backend server failed to start"
    cat /tmp/docmanager_test.log
    exit 1
fi

# ============================================================================
# TEST 3: Backend Health Check
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 3: Backend API Health${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

RESPONSE=$(curl -s "$BACKEND_URL/")
if echo "$RESPONSE" | grep -q "CA Desktop Backend Online"; then
    test_result 0 "Backend health endpoint responds correctly"
    echo "  Response: $RESPONSE"
else
    test_result 1 "Backend health endpoint failed"
fi

# ============================================================================
# TEST 4: API Documentation Accessible
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 4: API Documentation${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/docs")
if [ "$HTTP_CODE" = "200" ]; then
    test_result 0 "API documentation accessible at /docs"
else
    test_result 1 "API documentation not accessible (HTTP $HTTP_CODE)"
fi

# ============================================================================
# TEST 5: CA Login
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 5: CA Authentication${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

TOKEN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=lokesh&password=lokesh")

if echo "$TOKEN_RESPONSE" | grep -q "access_token"; then
    test_result 0 "CA login successful"
    TOKEN=$(echo "$TOKEN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")
    echo "  Token: ${TOKEN:0:30}..."
else
    test_result 1 "CA login failed"
    TOKEN=""
fi

# ============================================================================
# TEST 6: Authenticated API Calls
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 6: Authenticated API Endpoints${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if [ -n "$TOKEN" ]; then
    # Test clients endpoint
    CLIENTS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BACKEND_URL/api/v1/clients/")
    if echo "$CLIENTS_RESPONSE" | grep -q "\["; then
        CLIENT_COUNT=$(echo "$CLIENTS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
        test_result 0 "List clients endpoint works (found $CLIENT_COUNT clients)"
    else
        test_result 1 "List clients endpoint failed"
    fi
    
    # Test documents endpoint
    DOCS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BACKEND_URL/api/v1/documents/")
    if echo "$DOCS_RESPONSE" | grep -q "\["; then
        DOC_COUNT=$(echo "$DOCS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
        test_result 0 "List documents endpoint works (found $DOC_COUNT documents)"
    else
        test_result 1 "List documents endpoint failed"
    fi
    
    # Test reminders endpoint
    REMINDERS_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BACKEND_URL/api/v1/reminders/")
    if echo "$REMINDERS_RESPONSE" | grep -q "\["; then
        REMINDER_COUNT=$(echo "$REMINDERS_RESPONSE" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
        test_result 0 "List reminders endpoint works (found $REMINDER_COUNT reminders)"
    else
        test_result 1 "List reminders endpoint failed"
    fi
    
    # Test CA profile endpoint
    PROFILE_RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" "$BACKEND_URL/api/v1/profile/")
    if echo "$PROFILE_RESPONSE" | grep -q "firm_name"; then
        FIRM_NAME=$(echo "$PROFILE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('firm_name', 'N/A'))")
        test_result 0 "CA profile endpoint works (firm: $FIRM_NAME)"
    else
        test_result 1 "CA profile endpoint failed"
    fi
else
    test_result 1 "Skipping authenticated tests (no token)"
fi

# ============================================================================
# TEST 7: Public Endpoints
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 7: Public API Endpoints${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PUBLIC_PROFILE=$(curl -s "$BACKEND_URL/api/v1/public/ca/lokesh/profile")
if echo "$PUBLIC_PROFILE" | grep -q "ca_username"; then
    test_result 0 "Public CA profile endpoint works"
else
    test_result 1 "Public CA profile endpoint failed"
fi

PUBLIC_SERVICES=$(curl -s "$BACKEND_URL/api/v1/public/ca/lokesh/services")
if echo "$PUBLIC_SERVICES" | grep -q "\["; then
    SERVICE_COUNT=$(echo "$PUBLIC_SERVICES" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
    test_result 0 "Public services endpoint works (found $SERVICE_COUNT services)"
else
    test_result 1 "Public services endpoint failed"
fi

# ============================================================================
# TEST 8: Frontend Production Build
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 8: Frontend Production Build${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

FRONTEND_DIR="./dist_package/DocManager-v1.0.0/frontend"
if [ -f "$FRONTEND_DIR/index.html" ]; then
    test_result 0 "Frontend production build exists"
    BUNDLE_SIZE=$(du -sh "$FRONTEND_DIR" | cut -f1)
    echo "  Size: $BUNDLE_SIZE"
    
    # Check for main assets
    if [ -d "$FRONTEND_DIR/assets" ]; then
        ASSET_COUNT=$(ls -1 "$FRONTEND_DIR/assets" | wc -l)
        test_result 0 "Frontend assets directory exists ($ASSET_COUNT files)"
    else
        test_result 1 "Frontend assets directory missing"
    fi
else
    test_result 1 "Frontend production build not found"
fi

# ============================================================================
# TEST 9: Package Structure
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 9: Package Directory Structure${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

PKG_DIR="./dist_package/DocManager-v1.0.0"

# Check required directories
[ -d "$PKG_DIR/backend" ] && test_result 0 "backend/ directory exists" || test_result 1 "backend/ directory missing"
[ -d "$PKG_DIR/frontend" ] && test_result 0 "frontend/ directory exists" || test_result 1 "frontend/ directory missing"
[ -d "$PKG_DIR/data" ] && test_result 0 "data/ directory exists" || test_result 1 "data/ directory missing"
[ -d "$PKG_DIR/config" ] && test_result 0 "config/ directory exists" || test_result 1 "config/ directory missing"
[ -d "$PKG_DIR/scripts" ] && test_result 0 "scripts/ directory exists" || test_result 1 "scripts/ directory missing"

# Check required files
[ -f "$PKG_DIR/README.txt" ] && test_result 0 "README.txt exists" || test_result 1 "README.txt missing"
[ -f "$PKG_DIR/config/.env.template" ] && test_result 0 ".env.template exists" || test_result 1 ".env.template missing"
[ -f "$PKG_DIR/scripts/start_backend.bat" ] && test_result 0 "start_backend.bat exists" || test_result 1 "start_backend.bat missing"

# ============================================================================
# TEST 10: Memory Usage Check
# ============================================================================
echo ""
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo "${BLUE}TEST 10: Resource Usage${NC}"
echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

if ps -p $BACKEND_PID > /dev/null 2>&1; then
    MEMORY_KB=$(ps -o rss= -p $BACKEND_PID)
    MEMORY_MB=$((MEMORY_KB / 1024))
    echo "  Memory Usage: ${MEMORY_MB} MB"
    
    if [ $MEMORY_MB -lt 500 ]; then
        test_result 0 "Memory usage acceptable (< 500 MB)"
    else
        test_result 1 "Memory usage high (> 500 MB)"
    fi
    
    CPU_PERCENT=$(ps -o %cpu= -p $BACKEND_PID)
    echo "  CPU Usage: ${CPU_PERCENT}%"
else
    test_result 1 "Backend process not running"
fi

# ============================================================================
# SUMMARY
# ============================================================================
echo ""
echo "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo "${BLUE}║                      TEST SUMMARY                          ║${NC}"
echo "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""
echo "Total Tests: $TESTS_TOTAL"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

SUCCESS_RATE=$((TESTS_PASSED * 100 / TESTS_TOTAL))
echo ""
echo "Success Rate: ${SUCCESS_RATE}%"

if [ $SUCCESS_RATE -eq 100 ]; then
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          🎉 ALL TESTS PASSED! PACKAGE IS READY! 🎉         ║${NC}"
    echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
    exit 0
elif [ $SUCCESS_RATE -ge 80 ]; then
    echo ""
    echo -e "${YELLOW}⚠️  Most tests passed, but some issues need attention${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ CRITICAL: Multiple tests failed. Package needs fixes.${NC}"
    exit 1
fi
