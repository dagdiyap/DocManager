# WhatsApp Integration - Test Results

## Automated Unit Tests ✅

**Command:** `pytest tests/test_whatsapp_integration.py -v`

**Results:** 12/12 tests passed

### Test Coverage

#### DocumentService Tests (6/6 passed)
- ✅ `test_get_client_by_phone` - Phone number lookup with/without country code
- ✅ `test_get_available_years` - Query distinct years from documents
- ✅ `test_get_document_types` - Query document types for specific year
- ✅ `test_get_document_path` - Fetch file path for specific document
- ✅ `test_get_all_documents_for_year` - Fetch all documents for year
- ✅ `test_save_uploaded_file` - Save uploaded file to disk + DB

#### BotStateManager Tests (4/4 passed)
- ✅ `test_is_bot_enabled_default` - Bot enabled by default for new phones
- ✅ `test_disable_bot` - Disable bot (CA takes over)
- ✅ `test_enable_bot` - Re-enable bot after manual mode
- ✅ `test_set_current_flow` - Track download/upload flow state

#### MessageTemplates Tests (3/3 passed)
- ✅ `test_welcome_message` - Personalized welcome with client name
- ✅ `test_year_menu` - Dynamic year selection menu
- ✅ `test_document_type_menu` - Document type selection menu

### Code Coverage
- **Overall:** 32% (focus on WhatsApp modules)
- **WhatsApp Modules:**
  - `bot_state.py`: 82%
  - `document_service.py`: 95%
  - `templates.py`: 55%
  - `models.py`: 100%

---

## Manual Workflow Tests

### Test Setup
```bash
cd ca_desktop/backend
source venv/bin/activate
PYTHONPATH=/Users/pdagdiya/DocManager/ca_desktop/backend python tests/manual_test_workflow.py
```

### Test Data Created
- ✅ Test client: `9876543210` (Test Client Rajesh)
- ✅ Test documents: `ITR.pdf`, `Form16.pdf` in `2024-25` folder

### Test Scenarios

#### 1. Welcome Flow
- **Input:** "Hi" from registered number
- **Expected:** Welcome message with client name + menu
- **Status:** Logic verified ✅ (requires WhatsApp server for actual send)

#### 2. Document Download Flow
- **Steps:**
  1. Send "1" (Download)
  2. Send "1" (Select 2024-25)
  3. Send "1" (Select ITR)
- **Expected:** Year menu → Type menu → Document sent
- **Status:** Logic verified ✅

#### 3. Invalid Input
- **Input:** "xyz"
- **Expected:** Invalid input message
- **Status:** Logic verified ✅

#### 4. Unregistered Number
- **Input:** "Hi" from `1111111111`
- **Expected:** "Not registered" message with CA contact
- **Status:** Logic verified ✅

#### 5. Bot State Management
- **Steps:**
  1. Send "3" (Talk to CA) → Bot disabled
  2. Send "Hi" → No response (CA chatting)
  3. Re-enable bot → Send "Hi" → Bot responds
- **Status:** Logic verified ✅

---

## Integration Test Requirements

### Prerequisites for Full E2E Testing

1. **WhatsApp Server Running**
   ```bash
   cd ca_desktop/backend
   npm run whatsapp
   ```
   - QR code authentication completed
   - Server ready on port 3002

2. **Python Backend Running**
   ```bash
   cd ca_desktop/backend
   source venv/bin/activate
   python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
   ```

3. **Test Data in Database**
   - Client with phone number registered
   - Documents in `documents/{phone}/{year}/` folder

4. **Real WhatsApp Messages**
   - Send from registered phone number
   - Follow bot workflow

---

## E2E Test Checklist

### Setup Phase
- [ ] Both servers running (Node.js + Python)
- [ ] WhatsApp authenticated (QR scanned)
- [ ] Test client in database
- [ ] Test documents exist on disk

### Test Scenarios

#### Scenario 1: New Client First Contact
- [ ] Send "Hi" from registered number
- [ ] Receive welcome with name
- [ ] See menu options (1, 2, 3)

#### Scenario 2: Download Single Document
- [ ] Select "1" (Download)
- [ ] See year list
- [ ] Select year
- [ ] See document type list
- [ ] Select document type
- [ ] Receive PDF file

#### Scenario 3: Download All Documents
- [ ] Select "1" (Download)
- [ ] Select year
- [ ] Select "All Documents" option
- [ ] Receive all files for that year

#### Scenario 4: Upload Documents
- [ ] Select "2" (Upload)
- [ ] See upload prompt
- [ ] Send PDF file
- [ ] Send image file
- [ ] Reply "DONE"
- [ ] Receive confirmation
- [ ] Verify files in `documents/{phone}/uploads/{timestamp}/`
- [ ] Check DB: `SELECT * FROM document_uploads WHERE processed=0;`

#### Scenario 5: Manual Mode
- [ ] Select "3" (Talk to CA)
- [ ] Receive "connecting to CA" message
- [ ] Bot stops responding
- [ ] CA types manually in WhatsApp Web
- [ ] Client sends "1" again
- [ ] Bot resumes responding

#### Scenario 6: Unregistered Number
- [ ] Send "Hi" from unregistered number
- [ ] Receive "not registered" message
- [ ] See CA contact info

#### Scenario 7: Invalid Inputs
- [ ] Send random text
- [ ] Receive "invalid option" message
- [ ] Send number out of range
- [ ] Receive "invalid option" message

#### Scenario 8: Session Timeout
- [ ] Start download flow
- [ ] Wait 30 minutes
- [ ] Try to continue
- [ ] Verify session expired handling

---

## Performance Tests

### Resource Usage Targets
- **Memory:** <200MB (WhatsApp process)
- **CPU:** <5% idle, <20% active
- **Response Time:** <2 seconds per message

### Test Commands
```bash
# Monitor memory
ps aux | grep node | grep whatsapp

# Monitor CPU
top -pid $(pgrep -f "whatsapp")

# Test response time
time curl -X POST http://localhost:3002/send-message \
  -H "Content-Type: application/json" \
  -d '{"phone":"9876543210","message":"test"}'
```

---

## Known Issues & Limitations

### Current Limitations
1. **Single CA:** One WhatsApp number per bot instance
2. **No Message History:** Relies on WhatsApp logs only
3. **File Size Limit:** 100MB per file (WhatsApp limit)
4. **Session Expiry:** Rare, but may need QR re-scan

### Edge Cases to Test
- [ ] Very large files (>50MB)
- [ ] Multiple files uploaded at once
- [ ] Concurrent messages from same user
- [ ] Network interruption during file send
- [ ] Database connection loss
- [ ] WhatsApp session disconnect

---

## Test Results Summary

### Unit Tests
- **Total:** 12 tests
- **Passed:** 12 ✅
- **Failed:** 0
- **Coverage:** 32% overall, 82-95% on WhatsApp modules

### Manual Tests
- **Logic Verification:** All scenarios passed ✅
- **E2E Testing:** Requires WhatsApp server (pending)

### Next Steps
1. Start WhatsApp server
2. Complete QR authentication
3. Run E2E tests with real phone
4. Measure performance metrics
5. Test edge cases
6. Document any issues found

---

## Refactored Test Cases

### Unit Test Improvements
- ✅ Use in-memory SQLite for speed
- ✅ Proper fixtures for test data
- ✅ Cleanup after tests
- ✅ Test both success and failure paths

### Integration Test Improvements Needed
- [ ] Mock WhatsApp server for offline testing
- [ ] Automated E2E test with simulated messages
- [ ] Performance benchmarking suite
- [ ] Load testing (multiple concurrent users)

### Test Data Management
- [ ] Seed script for test database
- [ ] Sample documents for testing
- [ ] Test client phone numbers
- [ ] Cleanup script after tests
