# WhatsApp Bot - E2E Testing Guide

## Quick Start

### 1. Setup Test Data
```bash
cd ca_desktop/backend
source venv/bin/activate
python scripts/setup_test_data.py
```

### 2. Start Backend (Terminal 1)
```bash
cd ca_desktop/backend
source venv/bin/activate
PYTHONPATH=/Users/pdagdiya/DocManager python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8443
```

### 3. Start Mock WhatsApp Server (Terminal 2)
```bash
cd ca_desktop/backend
node src/services/whatsapp/mock_server.js
```

### 4. Run E2E Tests (Terminal 3)
```bash
cd ca_desktop/backend
source venv/bin/activate
python scripts/test_e2e_workflow.py
```

## What Gets Tested

### Test 1: Welcome Flow
- Client sends "Hi"
- Bot responds with personalized welcome message
- Shows menu: Download, Upload, Talk to CA

### Test 2: Document Download Flow
- Client selects "1" (Download)
- Bot shows year selection menu
- Client selects year
- Bot shows document type menu
- Client selects document type
- Bot sends document file

### Test 3: Invalid Input Handling
- Client sends invalid text ("xyz")
- Client sends invalid number ("99")
- Bot responds with error message

### Test 4: Unregistered Number
- Unknown number sends "Hi"
- Bot responds with "not registered" message
- Shows CA contact information

### Test 5: Bot State Management
- Client selects "3" (Talk to CA)
- Bot disables itself
- Client sends message - no bot response
- CA re-enables bot via API
- Bot responds again

## Test Results

All tests passed ✅

**Bot Messages Verified:**
- Welcome message with client name
- Year selection menu (dynamic from DB)
- Document type selection menu
- Invalid input error messages
- Unregistered number message
- Manual mode message
- Bot re-enabled confirmation

## Mock vs Real WhatsApp

### Mock Server (Current)
- No QR code needed
- No WhatsApp account needed
- Instant testing
- All bot messages printed to console
- Perfect for development

### Real WhatsApp Server
```bash
cd ca_desktop/backend
npm run whatsapp
```
- Requires QR code scan
- Needs WhatsApp account
- Real WhatsApp messages
- Full E2E with actual phone

## Files Created

- `scripts/setup_test_data.py` - Creates test client and documents
- `scripts/test_e2e_workflow.py` - E2E test automation
- `src/services/whatsapp/mock_server.js` - Mock WhatsApp server

## Test Data

**Client:**
- Phone: 9876543210
- Name: Test Client Rajesh

**Documents:**
- ITR.pdf (2024-25)
- Form16.pdf (2024-25)
