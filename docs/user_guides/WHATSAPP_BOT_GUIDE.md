# WhatsApp Bot - Guide for CA

## What It Does

Your clients can message your WhatsApp number and interact with an automated bot to:
1. **Download their documents** (ITR, Form 16, etc.)
2. **Upload documents** to your system (PAN card, bank statements, etc.)
3. **Request to talk to you directly** (bot steps aside)

Only clients registered in your system can use the bot. Unknown numbers are rejected automatically.

---

## How It Works for Clients

### Step 1: Client sends "Hi"
```
Client: Hi

Bot: 👋 Welcome Rajesh Patil!
     Reply with:
     1️⃣ Download Documents
     2️⃣ Upload Documents
     3️⃣ Talk to CA
     🌐 Website: https://ca-lokesh-dagdiya.vercel.app
```

### Step 2a: Download Documents
```
Client: 1

Bot: Select Year:
     1️⃣ 2024-25
     2️⃣ 2023-24

Client: 1

Bot: Select Document Type:
     1️⃣ ITR
     2️⃣ Form 16
     3️⃣ All Documents

Client: 1

Bot: 📄 Sending ITR...
     ✅ Document sent successfully!
```

The year list and document types are **generated automatically** from whatever documents you have stored for that client. If a client has no documents, they get a clear message.

### Step 2b: Upload Documents
```
Client: 2

Bot: 📤 Please send your documents (PDF, images, or zip files).
     When done, reply DONE.

Client: [Sends files via WhatsApp]

Bot: ✅ Received 2 file(s):
     - PAN_Card.pdf
     - Bank_Statement.pdf
     Uploading to CA's system... Done!
```

Uploaded files are saved to: `documents/{client_phone}/uploads/`

### Step 2c: Talk to CA
```
Client: 3

Bot: 📞 Connecting you to CA...
     You can now chat directly. CA will respond shortly.
```

The bot **stops responding** so you can chat with the client manually in WhatsApp Web. When done, re-enable the bot (see below).

---

## What You Need to Do

### Starting the Bot

Two things need to be running:

**1. Backend server** (manages data):
```
Already running if your desktop app is open.
```

**2. WhatsApp bot** (connects to WhatsApp):
```bash
cd ca_desktop/backend
npm run whatsapp
```

### First Time Only: Link Your WhatsApp

1. Run `npm run whatsapp`
2. A QR code appears in the terminal
3. On your phone: WhatsApp → Settings → Linked Devices → Link a Device
4. Scan the QR code
5. Wait for "Client is ready!" message

After first scan, the session is saved. You won't need to scan again unless you log out.

### Controlling the Bot

| Action | How |
|---|---|
| **Disable bot** (you want to chat manually) | Client selects "Talk to CA", or you call the disable API |
| **Re-enable bot** | Call the enable API from your system |
| **Check bot status** | Call the status API |

---

## What Happens with Different Users

| Scenario | Bot Response |
|---|---|
| **Registered active client** | Welcome message with menu |
| **Unregistered number** | "This number is not registered. Contact us at..." |
| **Inactive client** | "Your account is inactive. Please contact CA." |
| **Bot disabled for client** | No response (you're chatting manually) |

---

## Where Files Go

```
documents/
├── 9876543210/           ← Client phone number
│   ├── 2024-25/          ← Year folders (you manage these)
│   │   ├── ITR.pdf
│   │   └── Form16.pdf
│   └── uploads/          ← Client uploads via WhatsApp
│       └── 2026-03-02_10-30-15/
│           └── PAN_Card.pdf
```

- **Download**: Bot sends files from year folders
- **Upload**: Files saved to `uploads/` folder for you to review

---

## Troubleshooting

| Problem | Solution |
|---|---|
| Bot not responding | Check if both servers are running |
| Client says "not registered" | Add client to system with correct phone number |
| QR code not appearing | Restart `npm run whatsapp` |
| Need to re-link WhatsApp | Delete `.wwebjs_auth/` folder and restart |

---

## Important Notes

- **One WhatsApp number per CA** — the bot uses your personal/business WhatsApp
- **Only registered clients** can interact — others are rejected
- **Documents are local** — files stay on your computer, not uploaded to cloud
- **Bot is lightweight** — uses ~150-200MB memory when running
- **Session persists** — no need to re-scan QR code on restart
