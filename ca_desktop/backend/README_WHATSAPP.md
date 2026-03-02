# WhatsApp Bot - Developer Setup

## Architecture

```
WhatsApp ↔ Node.js (port 3002) ↔ Python Backend (port 8443)
            client.js/server.js     routers/whatsapp.py → handler.py
```

- **Node.js**: `whatsapp-web.js` client + Express HTTP bridge
- **Python**: FastAPI router → MessageHandler → DocumentService / BotStateManager

## Quick Start

### 1. Start Python Backend
```bash
cd ca_desktop/backend
source venv/bin/activate
PYTHONPATH=/path/to/DocManager python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8443
```

### 2. Start WhatsApp Server (Real)
```bash
cd ca_desktop/backend
npm run whatsapp
```
Scan QR code on first run. Session persists in `.wwebjs_auth/`.

### 2b. Start Mock Server (Testing)
```bash
cd ca_desktop/backend
node src/services/whatsapp/mock_server.js
```

## Testing

### Unit Tests
```bash
cd ca_desktop/backend
source venv/bin/activate
python -m pytest tests/test_production_ready.py -v
```

### E2E Tests
```bash
python scripts/test_comprehensive_e2e.py
```

### Setup Test Data
```bash
python scripts/setup_test_data.py
```

## API Endpoints

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/v1/whatsapp/incoming` | POST | Receive message from Node.js |
| `/api/v1/whatsapp/upload` | POST | Receive file upload from Node.js |
| `/api/v1/whatsapp/enable-bot/{phone}` | POST | Re-enable bot for a client |
| `/api/v1/whatsapp/disable-bot/{phone}` | POST | Disable bot (CA takes over) |
| `/api/v1/whatsapp/bot-status/{phone}` | GET | Check bot state |
| `/api/v1/whatsapp/uploads` | GET | List uploaded files |
| `/api/v1/whatsapp/uploads/{id}` | PATCH | Mark upload as processed |

## File Structure

```
src/services/whatsapp/
├── handler.py          # Message routing, conversation flow
├── document_service.py # DB queries, file operations
├── bot_state.py        # Bot enable/disable per client
├── templates.py        # All message templates
├── client.js           # whatsapp-web.js wrapper
├── server.js           # Express HTTP bridge (production)
└── mock_server.js      # Mock server (testing)
```

## Database Tables

- `whatsapp_bot_state` — bot enabled/disabled per phone, current flow, last interaction
- `document_uploads` — uploaded files: phone, filename, path, size, processed flag

## Security

- Only registered active clients (by phone number) can interact
- Inactive/unregistered numbers get rejection message
- File uploads validated (100MB limit, filename sanitized)
- Bot can be disabled per-client so CA can chat manually

## Troubleshooting

- **QR code not showing**: Check port 3002 is free, restart `npm run whatsapp`
- **Bot not responding**: Check both servers running, check `bot-status/{phone}`
- **Session expired**: Delete `.wwebjs_auth/`, restart, rescan QR
- **Client not found**: Verify client exists in DB with `is_active = true`
