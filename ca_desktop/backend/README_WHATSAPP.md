# WhatsApp Bot Integration - Setup Guide

## Overview

This WhatsApp bot provides a seamless document delivery system for CA clients. Clients can interact via WhatsApp to download documents, upload files, or talk directly to the CA.

## Architecture

- **Node.js Server** (`src/services/whatsapp/server.js`): Runs WhatsApp Web client
- **Python Backend** (`src/routers/whatsapp.py`): Handles business logic and database
- **Communication**: HTTP API between Node.js and Python

## Installation

### 1. Install Dependencies

Already installed:
- `whatsapp-web.js` - WhatsApp Web automation
- `qrcode-terminal` - QR code display for authentication

### 2. Database Setup

Already applied:
```bash
cd ca_desktop/backend
source venv/bin/activate
alembic upgrade head
```

Tables created:
- `document_uploads` - Track files uploaded via WhatsApp
- `whatsapp_bot_state` - Track bot enabled/disabled state per phone

## Usage

### Starting the WhatsApp Bot

**Terminal 1 - Start Python Backend:**
```bash
cd ca_desktop/backend
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Start WhatsApp Bot:**
```bash
cd ca_desktop/backend
npm run whatsapp
```

### First Time Setup

1. Start the WhatsApp bot server
2. A QR code will appear in the terminal
3. Open WhatsApp on your phone
4. Go to Settings → Linked Devices → Link a Device
5. Scan the QR code
6. Wait for "Client is ready!" message

### Session Persistence

The WhatsApp session is saved in `.wwebjs_auth/` directory. After first authentication:
- No need to scan QR code again on restart
- Session persists across server restarts
- Re-authentication only needed if session expires (rare)

## Client Workflow

### 1. Initial Contact
```
Client: Hi

Bot: 👋 Welcome Rajesh Patil!
     Reply with:
     1️⃣ Download Documents
     2️⃣ Upload Documents
     3️⃣ Talk to CA
     🌐 Website: https://ca-lokesh-dagdiya.vercel.app
```

### 2. Download Documents
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

Bot: 📄 Sending ITR...
     [Document sent]
     ✅ Document sent successfully!
```

### 3. Upload Documents
```
Client: 2

Bot: 📤 Please send your documents (PDF, images, or zip files).
     When done, reply DONE.

Client: [Sends files]

Bot: ✅ Received 3 file(s):
     - PAN_Card.pdf
     - Bank_Statement.pdf
     - Investment_Proof.jpg
     
     Uploading to CA's system... Done!
```

### 4. Talk to CA (Manual Mode)
```
Client: 3

Bot: 📞 Connecting you to CA...
     [Bot stops responding]

CA can now manually chat with client in WhatsApp Web.
```

## CA Controls

### View Uploaded Documents

**API Endpoint:**
```bash
GET http://localhost:8000/api/v1/whatsapp/uploads?processed=false
```

**Response:**
```json
{
  "uploads": [
    {
      "id": 1,
      "client_phone": "9876543210",
      "file_name": "PAN_Card.pdf",
      "file_size": 245678,
      "uploaded_at": "2026-03-02T10:30:00",
      "processed": false
    }
  ]
}
```

### Mark Upload as Processed

```bash
PATCH http://localhost:8000/api/v1/whatsapp/uploads/1
{
  "processed": true,
  "notes": "Moved to 2024-25 folder"
}
```

### Disable Bot (CA Takes Over)

```bash
POST http://localhost:8000/api/v1/whatsapp/disable-bot/9876543210
```

### Re-enable Bot

```bash
POST http://localhost:8000/api/v1/whatsapp/enable-bot/9876543210
```

### Check Bot Status

```bash
GET http://localhost:8000/api/v1/whatsapp/bot-status/9876543210
```

## File Locations

### Uploaded Files
```
documents/
└── {client_phone}/
    └── uploads/
        └── {timestamp}/
            ├── file1.pdf
            ├── file2.jpg
            └── metadata.json
```

Example:
```
documents/9876543210/uploads/2026-03-02_10-30-15/PAN_Card.pdf
```

### WhatsApp Session
```
ca_desktop/backend/.wwebjs_auth/
```

## Resource Usage

**Optimized for minimal resource consumption:**
- Memory: ~150-200MB (WhatsApp process)
- CPU: <5% idle, <20% during message handling
- Disk: ~50MB session data

## Troubleshooting

### QR Code Not Appearing
- Check if port 3002 is available
- Restart the WhatsApp bot server
- Check logs for errors

### Bot Not Responding
1. Check if WhatsApp bot server is running
2. Check if Python backend is running
3. Verify bot is enabled: `GET /api/v1/whatsapp/bot-status/{phone}`
4. Check logs in both terminals

### Session Expired
- Delete `.wwebjs_auth/` folder
- Restart WhatsApp bot server
- Scan QR code again

### Client Not Registered
- Verify client exists in database:
  ```sql
  SELECT * FROM clients WHERE phone_number = '9876543210';
  ```
- Add client if missing via CA dashboard

## Security

- **Phone Number Authentication**: Only registered clients can use bot
- **File Access Control**: Clients can only access their own documents
- **Bot Mode Control**: CA can disable bot anytime to chat manually
- **Audit Trail**: All uploads logged in database

## API Endpoints

### Incoming Message (Internal)
```
POST /api/v1/whatsapp/incoming
{
  "phone": "919876543210",
  "message": "Hi",
  "has_media": false,
  "message_id": "...",
  "timestamp": 1234567890
}
```

### Media Upload (Internal)
```
POST /api/v1/whatsapp/upload
Form Data:
- phone: "919876543210"
- file: [binary]
- mimetype: "application/pdf"
```

### Bot Control (CA)
```
POST /api/v1/whatsapp/enable-bot/{phone}
POST /api/v1/whatsapp/disable-bot/{phone}
GET /api/v1/whatsapp/bot-status/{phone}
```

### Upload Management (CA)
```
GET /api/v1/whatsapp/uploads?processed=false
PATCH /api/v1/whatsapp/uploads/{upload_id}
```

## Next Steps

1. **Test with Real Client**: Add test client to database and try workflow
2. **Desktop Notifications**: Add notifications when files uploaded
3. **Reminder Integration**: Connect to existing reminder system
4. **Multi-language**: Add Hindi/Marathi support
5. **Analytics**: Track usage metrics

## Production Deployment

For production, consider:
1. **Process Manager**: Use PM2 to keep WhatsApp bot running
2. **Monitoring**: Add health checks and alerts
3. **Backup**: Regular backup of `.wwebjs_auth/` session
4. **Scaling**: One WhatsApp bot per CA (separate phone numbers)

## Support

For issues or questions:
- Check logs in both terminals
- Review this documentation
- Contact development team
