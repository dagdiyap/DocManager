# WhatsApp Integration - Implementation State

## Decision Summary

**Chosen Approach**: Hybrid strategy
- **Phase 1**: whatsapp-web.js (browser-based, free, fast to implement)
- **Phase 2**: WhatsApp Business Cloud API (production-grade, scalable)

**Rationale**:
- whatsapp-web.js allows rapid prototyping and validation
- No upfront costs or Meta Business verification delays
- Can test complete workflow with real users immediately
- Easy migration path to official API later

---

## Architecture Decisions

### 1. WhatsApp Library: whatsapp-web.js
- **Why**: Free, feature-complete, good for single CA deployment
- **Risks**: Potential account blocks, requires QR re-auth
- **Mitigation**: Plan migration to official API in Phase 2

### 2. Session Management: Database-backed state machine
- **Why**: Reliable, persistent across restarts
- **Implementation**: `whatsapp_sessions` table with JSON context storage
- **States**: idle → authenticating → selecting_year → selecting_type → delivering

### 3. Authentication: PIN-based (4 digits)
- **Why**: Simpler for WhatsApp UX than full passwords
- **Security**: 3 attempts → 30-minute lockout
- **Storage**: Hashed in `clients.whatsapp_pin` column

### 4. Document Delivery: Direct file sending
- **Why**: WhatsApp supports PDF/images natively
- **Limits**: 100MB per file (WhatsApp limit)
- **Fallback**: Zip multiple files if needed

### 5. Menu System: Number-based selection
- **Why**: Easy to type on mobile, clear UX
- **Format**: "Reply with 1, 2, 3..." for all menus
- **Navigation**: Always provide back/exit options

---

## Database Schema Design

### whatsapp_sessions
```python
{
    "phone_number": "919876543210",  # WhatsApp number (with country code)
    "client_phone": "9876543210",     # Linked client (after auth)
    "session_state": "selecting_year",
    "context_data": {
        "selected_year": "2024-25",
        "menu_history": ["main", "download"],
        "auth_attempts": 0
    },
    "last_message_at": "2026-03-02T10:00:00",
    "expires_at": "2026-03-02T10:30:00"
}
```

### whatsapp_messages
- Full audit trail of all messages
- Supports debugging and analytics
- Track delivery status

---

## Workflow Implementation

### State Machine Flow
```
IDLE → (user sends "hi") → WELCOME
WELCOME → (user selects 1) → AUTHENTICATING
AUTHENTICATING → (PIN correct) → AUTHENTICATED
AUTHENTICATED → MAIN_MENU
MAIN_MENU → (user selects 1) → SELECTING_YEAR
SELECTING_YEAR → (user selects year) → SELECTING_TYPE
SELECTING_TYPE → (user selects type) → DELIVERING_DOCUMENT
DELIVERING_DOCUMENT → (success) → MAIN_MENU
```

### Message Templates
All templates stored in Python constants for easy modification:
- `WELCOME_MESSAGE`: Initial greeting + website link
- `AUTH_PROMPT`: PIN request
- `YEAR_MENU`: Dynamic list of available years
- `TYPE_MENU`: Document types for selected year
- `SUCCESS_MESSAGE`: Document sent confirmation
- `ERROR_MESSAGES`: Various error scenarios

---

## Integration Points

### 1. Existing Client System
- Use `clients.phone_number` for authentication
- Add `whatsapp_pin` column (nullable, for gradual rollout)
- Check `is_active` before allowing access

### 2. Existing Document System
- Query `documents` table by `client_phone` + `year` + `document_type`
- Use existing `FileStreamer` for secure file access
- Log downloads in `downloads` table

### 3. Existing Reminder System
- Extend `reminders` to support WhatsApp delivery
- Add `delivery_method` column: 'email', 'whatsapp', 'both'
- Scheduled job sends reminders via WhatsApp

---

## Technical Implementation Details

### WhatsApp Service Module Structure
```
ca_desktop/backend/src/services/whatsapp/
├── __init__.py
├── client.py          # WhatsApp client wrapper
├── session_manager.py # Session state management
├── message_handler.py # Incoming message router
├── menu_builder.py    # Menu generation
├── auth_service.py    # PIN authentication
├── document_service.py # Document search & delivery
└── templates.py       # Message templates
```

### Key Classes
1. **WhatsAppClient**: Manages whatsapp-web.js connection
2. **SessionManager**: CRUD operations on sessions table
3. **MessageHandler**: Routes messages to appropriate handlers
4. **MenuBuilder**: Generates dynamic menus based on data
5. **AuthService**: Handles PIN verification & lockouts
6. **DocumentService**: Searches & sends documents

---

## Security Measures

1. **Rate Limiting**: Max 10 messages/minute per user
2. **Session Timeout**: 30 minutes inactivity
3. **PIN Lockout**: 3 failed attempts → 30-minute block
4. **File Access Control**: Verify client ownership before sending
5. **Audit Logging**: All messages logged to database
6. **Input Sanitization**: Validate all user inputs

---

## Error Handling Strategy

### Network Errors
- Auto-reconnect WhatsApp client
- Queue messages during downtime
- Retry failed sends (3 attempts)

### User Errors
- Clear error messages in simple language
- Always provide way to return to main menu
- Timeout inactive sessions gracefully

### System Errors
- Log to file + database
- Alert CA via separate channel
- Graceful degradation (fallback to manual)

---

## Performance Considerations

1. **Message Queue**: In-memory queue for outbound messages
2. **Database Indexing**: Index on `phone_number`, `session_state`, `last_message_at`
3. **File Caching**: Cache frequently accessed documents
4. **Concurrent Handling**: Async message processing

---

## Monitoring & Observability

1. **Metrics to Track**:
   - Messages sent/received per hour
   - Authentication success rate
   - Document delivery success rate
   - Average response time
   - Active sessions count

2. **Logging**:
   - All WhatsApp events (connect, disconnect, message)
   - All user interactions (menu selections, downloads)
   - All errors with stack traces

3. **Alerts**:
   - WhatsApp disconnection
   - High error rate (>5% in 1 hour)
   - Failed document deliveries

---

## Migration Path to WhatsApp Business API

When ready for production scale:

1. **Setup**:
   - Create Meta Business account
   - Apply for WhatsApp Business API
   - Get phone number verified

2. **Code Changes**:
   - Replace whatsapp-web.js with official SDK
   - Implement webhook endpoint
   - Update message sending logic
   - Create message templates for approval

3. **Data Migration**:
   - No database changes needed
   - Update `whatsapp_messages` to store message IDs from API

4. **Benefits**:
   - No QR code re-authentication
   - Better reliability
   - Official support
   - Multi-agent support
   - Verified business badge

---

## Current Status

**Phase**: Planning Complete ✅

**Next Steps**:
1. Install whatsapp-web.js and dependencies
2. Create database migrations
3. Implement WhatsApp client wrapper
4. Build session management system
5. Implement authentication flow
6. Build menu system
7. Integrate document delivery
8. Testing with real data
9. Deploy and monitor

**Estimated Timeline**: 4-5 weeks for full implementation
