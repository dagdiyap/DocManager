#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         DocManager - Automated Service Testing            ║${NC}"
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo ""

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name - ${GREEN}OK${NC} (HTTP $response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $name - ${RED}FAILED${NC} (Expected $expected_code, got $response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# Function to test API endpoint with auth
test_api_endpoint() {
    local name=$1
    local url=$2
    local token=$3
    local expected_code=${4:-200}
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    if [ -n "$token" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $token" "$url" 2>/dev/null)
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    fi
    
    if [ "$response" -eq "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} $name - ${GREEN}OK${NC} (HTTP $response)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗${NC} $name - ${RED}FAILED${NC} (Expected $expected_code, got $response)"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

echo -e "${YELLOW}[1/5] Checking if services are running...${NC}"
echo ""

# Check backend
if curl -s http://localhost:8443/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Backend is running on port 8443"
else
    echo -e "${RED}✗${NC} Backend is NOT running on port 8443"
    echo -e "${YELLOW}Please run: ./start.sh${NC}"
    exit 1
fi

# Check frontend
if curl -s http://localhost:5174 > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Frontend is running on port 5174"
else
    echo -e "${RED}✗${NC} Frontend is NOT running on port 5174"
    echo -e "${YELLOW}Please run: ./start.sh${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[2/5] Testing Backend API Endpoints...${NC}"
echo ""

# Public endpoints
test_endpoint "API Health Check" "http://localhost:8443/docs"
test_endpoint "API Root" "http://localhost:8443/api/v1/" 404

# Auth endpoints
echo ""
echo -e "${BLUE}Authentication Endpoints:${NC}"

# Test CA login
echo -e "${YELLOW}Testing CA login...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8443/api/v1/auth/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=lokesh&password=lokesh" 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓${NC} CA Login - ${GREEN}OK${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    CA_TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
    echo -e "${BLUE}  Token obtained: ${CA_TOKEN:0:20}...${NC}"
else
    echo -e "${RED}✗${NC} CA Login - ${RED}FAILED${NC}"
    echo -e "${YELLOW}  Response: $LOGIN_RESPONSE${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    CA_TOKEN=""
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

# Test client login
echo -e "${YELLOW}Testing Client login...${NC}"
CLIENT_LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8443/api/v1/auth/client/login" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "username=9876543210&password=client123" 2>/dev/null)

if echo "$CLIENT_LOGIN_RESPONSE" | grep -q "access_token"; then
    echo -e "${GREEN}✓${NC} Client Login - ${GREEN}OK${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    CLIENT_TOKEN=$(echo "$CLIENT_LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
else
    echo -e "${RED}✗${NC} Client Login - ${RED}FAILED${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    CLIENT_TOKEN=""
fi
TOTAL_TESTS=$((TOTAL_TESTS + 1))

echo ""
echo -e "${BLUE}CA Protected Endpoints (with auth):${NC}"

if [ -n "$CA_TOKEN" ]; then
    test_api_endpoint "Get Clients List" "http://localhost:8443/api/v1/clients/" "$CA_TOKEN"
    test_api_endpoint "Get Documents List" "http://localhost:8443/api/v1/documents/" "$CA_TOKEN"
    test_api_endpoint "Get Reminders" "http://localhost:8443/api/v1/reminders/" "$CA_TOKEN"
    test_api_endpoint "Get CA Profile" "http://localhost:8443/api/v1/ca-profile/" "$CA_TOKEN"
    test_api_endpoint "Get Tags" "http://localhost:8443/api/v1/tags/" "$CA_TOKEN"
else
    echo -e "${YELLOW}⚠${NC} Skipping CA protected endpoints (no token)"
fi

echo ""
echo -e "${BLUE}Client Protected Endpoints (with auth):${NC}"

if [ -n "$CLIENT_TOKEN" ]; then
    test_api_endpoint "Client Documents" "http://localhost:8443/api/v1/client/documents/" "$CLIENT_TOKEN"
    test_api_endpoint "Client Profile" "http://localhost:8443/api/v1/client/profile/" "$CLIENT_TOKEN"
else
    echo -e "${YELLOW}⚠${NC} Skipping Client protected endpoints (no token)"
fi

echo ""
echo -e "${YELLOW}[3/5] Testing Frontend Routes...${NC}"
echo ""

test_endpoint "Frontend Root" "http://localhost:5174/"
test_endpoint "CA Login Page" "http://localhost:5174/ca/login"
test_endpoint "Client Login Page" "http://localhost:5174/portal/login"
test_endpoint "Public CA Page" "http://localhost:5174/ca-lokesh-dagdiya"

echo ""
echo -e "${YELLOW}[4/5] Testing Database...${NC}"
echo ""

if [ -f "ca_desktop.db" ]; then
    echo -e "${GREEN}✓${NC} Database file exists"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    
    # Check if database has tables
    TABLE_COUNT=$(sqlite3 ca_desktop.db "SELECT COUNT(*) FROM sqlite_master WHERE type='table';" 2>/dev/null)
    if [ "$TABLE_COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓${NC} Database has $TABLE_COUNT tables"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗${NC} Database has no tables"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    
    # Check for demo data
    CA_COUNT=$(sqlite3 ca_desktop.db "SELECT COUNT(*) FROM users;" 2>/dev/null)
    CLIENT_COUNT=$(sqlite3 ca_desktop.db "SELECT COUNT(*) FROM clients;" 2>/dev/null)
    
    echo -e "${BLUE}  CA Users: $CA_COUNT${NC}"
    echo -e "${BLUE}  Clients: $CLIENT_COUNT${NC}"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 2))
else
    echo -e "${RED}✗${NC} Database file not found"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo -e "${YELLOW}[5/5] Testing Key Workflows...${NC}"
echo ""

# Test creating a client
if [ -n "$CA_TOKEN" ]; then
    echo -e "${YELLOW}Testing: Create new client...${NC}"
    CREATE_CLIENT=$(curl -s -X POST "http://localhost:8443/api/v1/clients/" \
        -H "Authorization: Bearer $CA_TOKEN" \
        -H "Content-Type: application/json" \
        -d '{
            "name": "Test Client",
            "phone": "9999999999",
            "email": "test@example.com",
            "pan": "AAAAA0000A",
            "aadhar": "999999999999"
        }' 2>/dev/null)
    
    if echo "$CREATE_CLIENT" | grep -q '"id"'; then
        echo -e "${GREEN}✓${NC} Create Client - ${GREEN}OK${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TEST_CLIENT_ID=$(echo "$CREATE_CLIENT" | grep -o '"id":[0-9]*' | cut -d':' -f2)
        echo -e "${BLUE}  Created client ID: $TEST_CLIENT_ID${NC}"
        
        # Clean up - delete test client
        curl -s -X DELETE "http://localhost:8443/api/v1/clients/$TEST_CLIENT_ID" \
            -H "Authorization: Bearer $CA_TOKEN" > /dev/null 2>&1
        echo -e "${BLUE}  Cleaned up test client${NC}"
    else
        echo -e "${RED}✗${NC} Create Client - ${RED}FAILED${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

echo ""
echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     Test Summary                           ║${NC}"
echo -e "${BLUE}╠════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║${NC} Total Tests:  $TOTAL_TESTS"
echo -e "${BLUE}║${NC} ${GREEN}Passed:       $PASSED_TESTS${NC}"
echo -e "${BLUE}║${NC} ${RED}Failed:       $FAILED_TESTS${NC}"
echo -e "${BLUE}║${NC}"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${BLUE}║${NC} ${GREEN}Status:       ALL TESTS PASSED ✓${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}🎉 All services are working correctly!${NC}"
    echo ""
    echo -e "${BLUE}You can now:${NC}"
    echo -e "  1. Login as CA: http://localhost:5174/ca/login (lokesh/lokesh)"
    echo -e "  2. Add clients, upload documents, set reminders"
    echo -e "  3. Login as Client: http://localhost:5174/portal/login (9876543210/client123)"
    echo -e "  4. Download documents from client portal"
    echo ""
    exit 0
else
    echo -e "${BLUE}║${NC} ${RED}Status:       SOME TESTS FAILED ✗${NC}"
    echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}⚠ Some tests failed. Please check the output above.${NC}"
    echo ""
    exit 1
fi
