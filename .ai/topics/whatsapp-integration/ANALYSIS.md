# WhatsApp Integration - Architecture Analysis & Planning

## Current Architecture Overview

### Database Schema
- **Client Model**: `phone_number` (unique), `name`, `password_hash`, `email`, `client_type`, `is_active`
- **Document Model**: `client_phone`, `year`, `document_type`, `file_name`, `file_path`, `file_size`
- **DocumentTag Model**: Tag-based categorization (ITR, Form 16, etc.)
- **Reminder Model**: Existing reminder system for clients

### Existing Systems
1. **Authentication**: Phone + password based
2. **Document Management**: Year-based, type-based organization
3. **Reminder System**: Already exists for notifications
4. **File Serving**: FileStreamer with path traversal protection

---

## WhatsApp SDK Selection Analysis

### Option 1: Browser-Based SDKs (whatsapp-web.js, Baileys)
**Pros:**
- Free, no API costs
- Full WhatsApp Web features
- Can send media files directly
- No Meta Business verification needed
- Quick to set up

**Cons:**
- Requires browser/headless Chrome running 24/7
- QR code re-authentication periodically
- Can be blocked by WhatsApp if detected as bot
- Less stable for production
- Single device limitation
- Risk of account ban

**Best for:** Testing, small-scale deployments, single CA

### Option 2: Official WhatsApp Business API (Cloud API)
**Pros:**
- Official, stable, production-grade
- No risk of account ban
- Supports multiple agents
- Webhook-based (no polling)
- Better deliverability
- Message templates for notifications
- Verified business profile

**Cons:**
- Requires Meta Business verification
- Costs per conversation (free tier: 1000 conversations/month)
- Template approval process for notifications
- More complex setup
- Requires HTTPS webhook endpoint

**Best for:** Production, scalability, multiple CAs, long-term

### Option 3: Third-Party APIs (Twilio, MessageBird, etc.)
**Pros:**
- Managed infrastructure
- Good documentation
- Additional features (SMS fallback)

**Cons:**
- Higher costs
- Vendor lock-in
- Still requires WhatsApp Business API setup

---

## RECOMMENDATION: Hybrid Approach

### Phase 1 (Immediate): whatsapp-web.js
- Fast implementation
- Test workflows with real users
- Validate chatbot UX
- No costs

### Phase 2 (Production): WhatsApp Business Cloud API
- Migrate to official API
- Scale to multiple CAs
- Add advanced features
- Production-grade reliability

---

## WhatsApp Chatbot Workflow Design

### 1. Initial Contact Flow
```
User: Hi
Bot: 
👋 Welcome to Dagdiya Associates!

I'm your document assistant. I can help you:
• Download your tax documents
• Check document status
• Get reminders

🌐 Visit: https://ca-lokesh-dagdiya.vercel.app

Reply with a number:
1️⃣ Download Documents
2️⃣ Check Status
3️⃣ Talk to CA
```

### 2. Authentication Flow
```
Bot: Please enter your registered phone number
User: 9876543210
Bot: Enter your 4-digit PIN (or type FORGOT)
User: 1234
Bot: ✅ Authenticated as Rajesh Patil
```

### 3. Document Selection Flow
```
Bot: Select Year:
1️⃣ 2024-25
2️⃣ 2023-24
3️⃣ 2022-23
4️⃣ 2021-22

User: 1

Bot: Select Document Type:
1️⃣ ITR (Income Tax Return)
2️⃣ Form 16
3️⃣ TDS Certificate
4️⃣ Audit Report
5️⃣ All Documents

User: 1

Bot: 📄 Sending ITR_2024-25.pdf...
[Document sent]
✅ Document sent successfully!

Need anything else?
1️⃣ Download more documents
2️⃣ Main menu
3️⃣ Exit
```

### 4. Reminder Flow (Automated)
```
Bot: 🔔 Reminder: ITR Filing Deadline

Dear Rajesh Patil,

Your ITR filing deadline is in 7 days (31st July).

Documents ready:
✅ Form 16
✅ Bank Statements
❌ Investment Proofs (pending)

Reply:
1️⃣ Download documents
2️⃣ Upload proofs
3️⃣ Talk to CA
```

---

## Database Schema Changes

### New Table: `whatsapp_sessions`
```sql
CREATE TABLE whatsapp_sessions (
    id INTEGER PRIMARY KEY,
    phone_number VARCHAR(15) UNIQUE NOT NULL,
    client_phone VARCHAR(15) REFERENCES clients(phone_number),
    session_state VARCHAR(50) NOT NULL,  -- 'idle', 'authenticating', 'selecting_year', 'selecting_type'
    context_data JSON,  -- Store current selection context
    last_message_at DATETIME,
    created_at DATETIME,
    expires_at DATETIME
);
```

### New Table: `whatsapp_messages`
```sql
CREATE TABLE whatsapp_messages (
    id INTEGER PRIMARY KEY,
    phone_number VARCHAR(15) NOT NULL,
    message_id VARCHAR(255) UNIQUE,
    direction VARCHAR(10) NOT NULL,  -- 'inbound', 'outbound'
    message_type VARCHAR(20),  -- 'text', 'document', 'image'
    content TEXT,
    media_url TEXT,
    status VARCHAR(20),  -- 'sent', 'delivered', 'read', 'failed'
    created_at DATETIME
);
```

### Update Client Table
```sql
ALTER TABLE clients ADD COLUMN whatsapp_pin VARCHAR(4);
ALTER TABLE clients ADD COLUMN whatsapp_enabled BOOLEAN DEFAULT TRUE;
ALTER TABLE clients ADD COLUMN last_whatsapp_interaction DATETIME;
```

---

## Edge Cases & Error Handling

### 1. Authentication Failures
- **Invalid PIN**: 3 attempts → lock for 30 minutes
- **Unregistered number**: Provide CA contact info
- **Expired session**: Auto-logout after 30 minutes inactivity

### 2. Document Not Found
- **No documents for year**: Suggest other years
- **Document type not available**: Show available types
- **File missing**: Alert CA, log error

### 3. Network/System Failures
- **WhatsApp disconnected**: Auto-reconnect, queue messages
- **File upload failure**: Retry 3 times, then manual intervention
- **Database error**: Graceful error message, log for CA

### 4. Invalid Input
- **Non-numeric input**: "Please reply with a number (1-4)"
- **Out of range**: "Invalid option. Please choose 1-4"
- **Timeout**: "Session expired. Type HI to start again"

### 5. Concurrent Sessions
- **Multiple devices**: Allow, but warn about security
- **Session conflicts**: Last active session wins

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Set up whatsapp-web.js
- [ ] Create WhatsApp service module
- [ ] Implement QR code authentication
- [ ] Basic message sending/receiving
- [ ] Database schema migration

### Phase 2: Core Chatbot (Week 2)
- [ ] Session management system
- [ ] State machine for conversation flow
- [ ] Authentication workflow (PIN-based)
- [ ] Menu system (year selection, type selection)
- [ ] Message templates

### Phase 3: Document Delivery (Week 3)
- [ ] Document search by year + type
- [ ] File retrieval from FileStreamer
- [ ] WhatsApp document sending
- [ ] Download tracking
- [ ] Error handling & retries

### Phase 4: Reminders Integration (Week 4)
- [ ] Connect to existing reminder system
- [ ] Scheduled reminder messages
- [ ] Bulk reminder sending
- [ ] Reminder acknowledgment tracking

### Phase 5: Advanced Features (Week 5+)
- [ ] Multi-language support
- [ ] Document upload via WhatsApp
- [ ] Payment reminders
- [ ] Analytics dashboard
- [ ] Migration to WhatsApp Business API

---

## Technical Stack

### Backend
- **Language**: Python 3.14
- **Framework**: FastAPI (existing)
- **WhatsApp Library**: whatsapp-web.js (Phase 1) → WhatsApp Business Cloud API (Phase 2)
- **Database**: SQLite (existing)
- **Message Queue**: In-memory queue → Redis (for production)

### Infrastructure
- **WhatsApp Session**: Runs on CA's laptop (same as backend)
- **Webhook**: Cloudflare Tunnel (existing setup)
- **File Storage**: Local filesystem (existing)

---

## Security Considerations

1. **PIN-based Auth**: 4-digit PIN (simpler than password for WhatsApp)
2. **Session Timeout**: 30 minutes inactivity
3. **Rate Limiting**: Max 10 messages per minute per user
4. **File Access Control**: Verify client ownership before sending
5. **Audit Logging**: Log all WhatsApp interactions
6. **Encryption**: WhatsApp E2E encryption (built-in)

---

## Success Metrics

1. **Adoption Rate**: % of clients using WhatsApp vs web portal
2. **Response Time**: Average time to deliver document
3. **Error Rate**: Failed document deliveries
4. **User Satisfaction**: Feedback after interaction
5. **CA Efficiency**: Time saved vs manual document sending

---

## Next Steps

1. ✅ Complete architecture analysis
2. Create detailed implementation plan for Phase 1
3. Set up whatsapp-web.js development environment
4. Implement database migrations
5. Build core WhatsApp service module
6. Implement authentication workflow
7. Build menu-based document selection
8. Integrate with existing document system
9. Testing with real client data
10. Deploy and monitor
