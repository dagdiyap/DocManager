# WhatsApp Integration - Refactored MVP Plan

## Key Changes from Original Plan

### REMOVED Features
- ❌ Password/PIN authentication (use phone number only)
- ❌ Session state tracking (rely on WhatsApp logs)
- ❌ Messaging capability (document delivery only)
- ❌ whatsapp_sessions table (not needed)
- ❌ Complex state machine

### ADDED Features
- ✅ Document upload from WhatsApp → CA desktop
- ✅ Bot mode exit for CA manual messaging
- ✅ Resource-optimized browser automation
- ✅ Seamless phone number-based authentication

---

## Architecture Overview

### Core Principle
**Lightweight, resource-efficient WhatsApp automation that acts as a document delivery bot**

### Technology Stack
- **WhatsApp Library**: `whatsapp-web.js` with optimized Puppeteer settings
- **Browser**: Headless Chrome with minimal flags
- **Memory Target**: <200MB for WhatsApp process
- **CPU Target**: <5% idle, <20% during message handling

---

## Simplified Workflow

### 1. Client Initiates (No Authentication Required)
```
Client: Hi
Bot: 👋 Welcome Rajesh Patil! (auto-detected from phone)
     
     Reply with:
     1️⃣ Download Documents
     2️⃣ Upload Documents
     3️⃣ Talk to CA
```

**Logic:**
- Incoming message from `+919876543210`
- Query DB: `SELECT * FROM clients WHERE phone_number = '9876543210'`
- If found: Show personalized menu with client name
- If not found: "This number is not registered. Please contact CA at +91 98901 54945"

### 2. Document Download Flow
```
Client: 1

Bot: Select Year:
     1️⃣ 2024-25
     2️⃣ 2023-24
     3️⃣ 2022-23

Client: 1

Bot: Select Document Type:
     1️⃣ ITR
     2️⃣ Form 16
     3️⃣ TDS Certificate
     4️⃣ All Documents

Client: 1

Bot: 📄 Sending ITR_2024-25.pdf...
     [Document sent]
     ✅ Done! Need anything else? Reply 1 for more documents.
```

### 3. Document Upload Flow
```
Client: 2

Bot: Please send your documents (PDF, images, or zip files).
     When done, reply DONE.

Client: [Sends 3 files]

Bot: ✅ Received 3 files:
     - PAN_Card.pdf
     - Bank_Statement.pdf
     - Investment_Proof.jpg
     
     Uploading to CA's system...
     ✅ Upload complete! CA will review shortly.
```

**Logic:**
- Files saved to: `documents/{client_phone}/uploads/{timestamp}/`
- DB entry created in `document_uploads` table
- CA gets desktop notification

### 4. Talk to CA (Exit Bot Mode)
```
Client: 3

Bot: 📞 Connecting you to CA...
     [Bot mode disabled for this chat]
     
CA can now manually message the client.
Bot will not auto-respond until client sends "1" or "2" again.
```

---

## Database Schema (Simplified)

### Existing Table: `clients`
```sql
-- No changes needed, use as-is
phone_number VARCHAR(15) PRIMARY KEY
name VARCHAR(255)
email VARCHAR(255)
client_type VARCHAR(50)
is_active BOOLEAN
```

### New Table: `document_uploads`
```sql
CREATE TABLE document_uploads (
    id INTEGER PRIMARY KEY,
    client_phone VARCHAR(15) NOT NULL REFERENCES clients(phone_number),
    file_name VARCHAR(255) NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    processed BOOLEAN DEFAULT FALSE,
    notes TEXT
);
CREATE INDEX idx_uploads_client ON document_uploads(client_phone);
CREATE INDEX idx_uploads_processed ON document_uploads(processed);
```

### New Table: `whatsapp_bot_state` (Minimal)
```sql
CREATE TABLE whatsapp_bot_state (
    phone_number VARCHAR(15) PRIMARY KEY,
    bot_enabled BOOLEAN DEFAULT TRUE,  -- False when CA takes over
    last_interaction DATETIME,
    current_flow VARCHAR(50)  -- 'download', 'upload', 'manual', NULL
);
```

**Purpose**: Only track if bot is active or CA is manually chatting. No complex state.

---

## Resource Optimization Strategy

### 1. Puppeteer Configuration
```javascript
{
  headless: true,
  args: [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-dev-shm-usage',
    '--disable-accelerated-2d-canvas',
    '--no-first-run',
    '--no-zygote',
    '--disable-gpu',
    '--disable-software-rasterizer',
    '--disable-extensions',
    '--disable-background-networking',
    '--disable-default-apps',
    '--disable-sync',
    '--metrics-recording-only',
    '--mute-audio',
    '--no-default-browser-check'
  ],
  defaultViewport: { width: 800, height: 600 },  // Minimal viewport
}
```

### 2. Memory Management
- **Session persistence**: Save WhatsApp session to disk, reuse on restart
- **Message queue**: Process messages sequentially (no parallel processing)
- **File streaming**: Stream large files instead of loading into memory
- **Garbage collection**: Explicit cleanup after each message

### 3. CPU Optimization
- **Event-driven**: Only process when message arrives (no polling)
- **Lazy loading**: Load document list only when requested
- **Caching**: Cache client info for 5 minutes to reduce DB queries
- **Debouncing**: Wait 1 second before responding (batch rapid messages)

---

## Implementation Modules

### Module 1: WhatsApp Client (Lightweight)
```python
# ca_desktop/backend/src/services/whatsapp/client.py

class WhatsAppClient:
    """Lightweight WhatsApp Web client wrapper."""
    
    def __init__(self):
        self.client = None
        self.is_ready = False
        
    async def initialize(self):
        """Start WhatsApp client with optimized settings."""
        # Launch with minimal resources
        # Save session for reuse
        
    async def send_message(self, phone: str, text: str):
        """Send text message."""
        
    async def send_document(self, phone: str, file_path: str, caption: str):
        """Send document file."""
        
    async def on_message(self, callback):
        """Register message handler."""
```

### Module 2: Message Handler (Simple Router)
```python
# ca_desktop/backend/src/services/whatsapp/handler.py

class MessageHandler:
    """Routes incoming messages to appropriate handlers."""
    
    async def handle_message(self, message):
        phone = message.from_phone
        text = message.body
        
        # Check if bot is enabled for this chat
        bot_state = get_bot_state(phone)
        if not bot_state.bot_enabled:
            return  # CA is manually chatting
        
        # Check if client exists
        client = get_client_by_phone(phone)
        if not client:
            await send_unregistered_message(phone)
            return
        
        # Route based on message content
        if text.lower() in ['hi', 'hello', 'start']:
            await send_welcome_menu(phone, client.name)
        elif text == '1':
            await handle_download_flow(phone, client)
        elif text == '2':
            await handle_upload_flow(phone, client)
        elif text == '3':
            await disable_bot_mode(phone)
        else:
            await send_invalid_input_message(phone)
```

### Module 3: Document Service
```python
# ca_desktop/backend/src/services/whatsapp/documents.py

class DocumentService:
    """Handle document download and upload."""
    
    async def get_available_years(self, client_phone: str) -> list[str]:
        """Query distinct years from documents table."""
        
    async def get_document_types(self, client_phone: str, year: str) -> list[str]:
        """Query distinct document types for year."""
        
    async def fetch_document(self, client_phone: str, year: str, doc_type: str) -> str:
        """Get file path for document."""
        
    async def save_uploaded_file(self, client_phone: str, file_data: bytes, 
                                 file_name: str) -> str:
        """Save uploaded file to disk and DB."""
```

### Module 4: Bot State Manager
```python
# ca_desktop/backend/src/services/whatsapp/bot_state.py

class BotStateManager:
    """Minimal state tracking."""
    
    def is_bot_enabled(self, phone: str) -> bool:
        """Check if bot should respond or CA is chatting."""
        
    def disable_bot(self, phone: str):
        """CA takes over chat manually."""
        
    def enable_bot(self, phone: str):
        """Re-enable bot for this chat."""
        
    def set_current_flow(self, phone: str, flow: str):
        """Track if user is in download/upload flow."""
```

---

## File Upload Implementation

### Upload Directory Structure
```
documents/
├── 9876543210/
│   ├── 2024-25/
│   │   ├── ITR.pdf
│   │   └── Form16.pdf
│   └── uploads/
│       ├── 2026-03-02_10-30-15/
│       │   ├── PAN_Card.pdf
│       │   ├── Bank_Statement.pdf
│       │   └── metadata.json
│       └── 2026-03-01_15-45-30/
│           └── Investment_Proof.jpg
```

### Upload Workflow
1. Client sends file(s) via WhatsApp
2. Bot receives file, downloads to temp location
3. Move to `documents/{client_phone}/uploads/{timestamp}/`
4. Create DB entry in `document_uploads`
5. Send confirmation to client
6. Notify CA via desktop notification

### CA Review Process
- CA opens desktop app
- Sees "New Uploads" notification
- Reviews files in uploads folder
- Can move to proper year/type folder
- Marks as "processed" in DB

---

## Bot Mode Exit Mechanism

### CA-Side Interface (Desktop App)
```
WhatsApp Chat Monitor:
┌─────────────────────────────────────┐
│ Active Chats:                       │
│                                     │
│ 📱 Rajesh Patil (9876543210)       │
│    Status: [BOT MODE] 🤖           │
│    Last: "Downloaded ITR" (2m ago) │
│    [Take Over Manually]            │
│                                     │
│ 📱 Priya Shah (9988776655)         │
│    Status: [MANUAL MODE] 👤        │
│    Last: "Thanks!" (5m ago)        │
│    [Enable Bot]                    │
└─────────────────────────────────────┘
```

### Implementation
- CA clicks "Take Over Manually" → `bot_enabled = FALSE` in DB
- Bot stops auto-responding for that chat
- CA can type normally in WhatsApp Web
- Client can also trigger manual mode by selecting "3️⃣ Talk to CA"
- Bot re-enables when client sends "1" or "2" again

---

## Message Templates (Simplified)

```python
WELCOME_MESSAGE = """
👋 Welcome {name}!

Reply with:
1️⃣ Download Documents
2️⃣ Upload Documents  
3️⃣ Talk to CA

🌐 Website: https://ca-lokesh-dagdiya.vercel.app
"""

UNREGISTERED_MESSAGE = """
This number is not registered with Dagdiya Associates.

Please contact us:
📞 +91 98901 54945
📧 lokeshdagdiya@gmail.com
"""

YEAR_MENU = """
Select Year:
{year_options}
"""

TYPE_MENU = """
Select Document Type:
{type_options}
"""

UPLOAD_PROMPT = """
📤 Please send your documents (PDF, images, or zip files).

When done, reply DONE.
"""

UPLOAD_CONFIRMATION = """
✅ Received {count} file(s):
{file_list}

Uploading to CA's system... Done!
CA will review shortly.
"""

MANUAL_MODE_MESSAGE = """
📞 Connecting you to CA...

You can now chat directly. CA will respond shortly.
"""

INVALID_INPUT = """
Invalid option. Please reply with a number (1, 2, or 3).
"""
```

---

## Performance Targets

### Resource Usage (Per CA)
- **Memory**: <200MB for WhatsApp process
- **CPU**: <5% idle, <20% during active message handling
- **Disk**: Session data ~50MB, logs ~10MB/day
- **Network**: Minimal (only when messages sent/received)

### Response Times
- **Welcome message**: <2 seconds
- **Menu generation**: <1 second (cached)
- **Document send**: <5 seconds for <10MB file
- **Upload save**: <3 seconds per file

### Scalability
- **Concurrent chats**: Up to 50 active conversations
- **Messages/hour**: Up to 500 (10 messages/min average)
- **File uploads/day**: Up to 100 files

---

## Implementation Phases (Revised)

### Phase 1: Core Bot (Week 1)
- [ ] Install whatsapp-web.js with optimized Puppeteer
- [ ] Implement WhatsAppClient with resource optimization
- [ ] Database migration (document_uploads, whatsapp_bot_state)
- [ ] Basic message handler (welcome, menu routing)
- [ ] Phone number authentication (DB lookup only)

### Phase 2: Document Download (Week 2)
- [ ] Year selection menu (dynamic from DB)
- [ ] Document type selection menu
- [ ] Document fetch from FileStreamer
- [ ] WhatsApp document sending
- [ ] Error handling

### Phase 3: Document Upload (Week 3)
- [ ] File reception from WhatsApp
- [ ] Save to uploads folder
- [ ] DB tracking (document_uploads table)
- [ ] Desktop notification for CA
- [ ] Upload confirmation messages

### Phase 4: Bot Mode Control (Week 4)
- [ ] Bot state management
- [ ] CA manual takeover interface
- [ ] "Talk to CA" option for clients
- [ ] Bot re-enable logic
- [ ] Testing with real scenarios

---

## Testing Strategy

### Unit Tests
- Phone number lookup
- Menu generation
- File path validation
- Upload directory creation

### Integration Tests
- WhatsApp message flow
- Document retrieval
- File upload end-to-end
- Bot enable/disable

### Performance Tests
- Memory usage under load
- CPU usage during file transfers
- Response time benchmarks
- Concurrent chat handling

---

## Deployment Checklist

- [ ] WhatsApp Web QR code scanned
- [ ] Session persisted to disk
- [ ] Database migrations applied
- [ ] Upload directories created with permissions
- [ ] Desktop notification system working
- [ ] Resource monitoring enabled
- [ ] Backup strategy for WhatsApp session
- [ ] CA training on bot mode control

---

## Success Criteria

1. **Resource Efficiency**: WhatsApp process uses <200MB RAM
2. **Response Time**: Bot responds within 2 seconds
3. **Reliability**: 99% uptime during business hours
4. **User Experience**: Clients can download documents in <30 seconds
5. **CA Efficiency**: 80% reduction in manual document sending time
