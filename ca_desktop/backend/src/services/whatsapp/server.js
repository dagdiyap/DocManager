/**
 * WhatsApp bot server - Bridge between Node.js WhatsApp client and Python backend.
 * 
 * This server runs the WhatsApp Web client and exposes a simple HTTP API
 * for the Python backend to send/receive messages.
 */

const express = require('express');
const bodyParser = require('body-parser');
const WhatsAppClient = require('./client');

const app = express();
app.use(bodyParser.json());

const whatsappClient = new WhatsAppClient();
let pythonBackendUrl = process.env.BACKEND_URL || 'http://localhost:8443';

// Store for pending responses (simple in-memory queue)
const messageQueue = [];

/**
 * Initialize WhatsApp client on server start.
 */
async function initializeWhatsApp() {
    try {
        await whatsappClient.initialize();
        
        // Register message handler to forward to Python backend
        whatsappClient.onMessage(async (msgData, rawMessage) => {
            try {
                // Forward message to Python backend
                const response = await fetch(`${pythonBackendUrl}/api/v1/whatsapp/incoming`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        phone: msgData.from,
                        message: msgData.body,
                        has_media: msgData.hasMedia,
                        message_id: msgData.id,
                        timestamp: msgData.timestamp
                    })
                });

                if (!response.ok) {
                    console.error('[Server] Error forwarding message to Python backend:', response.statusText);
                }

                // If message has media, download and forward
                if (msgData.hasMedia) {
                    const media = await whatsappClient.downloadMedia(rawMessage);
                    if (media) {
                        // Forward media to Python backend
                        const formData = new FormData();
                        formData.append('phone', msgData.from);
                        formData.append('file', new Blob([media.data]), media.filename);
                        formData.append('mimetype', media.mimetype);

                        await fetch(`${pythonBackendUrl}/api/v1/whatsapp/upload`, {
                            method: 'POST',
                            body: formData
                        });
                    }
                }
            } catch (error) {
                console.error('[Server] Error processing incoming message:', error);
            }
        });

        console.log('[Server] WhatsApp client initialized successfully');
    } catch (error) {
        console.error('[Server] Failed to initialize WhatsApp client:', error);
        process.exit(1);
    }
}

/**
 * Health check endpoint.
 */
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        whatsapp_ready: whatsappClient.isReady
    });
});

/**
 * Send text message endpoint.
 */
app.post('/send-message', async (req, res) => {
    try {
        const { phone, message } = req.body;

        if (!phone || !message) {
            return res.status(400).json({ error: 'Phone and message are required' });
        }

        await whatsappClient.sendMessage(phone, message);
        res.json({ success: true });
    } catch (error) {
        console.error('[Server] Error sending message:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Send document endpoint.
 */
app.post('/send-document', async (req, res) => {
    try {
        const { phone, file_path, caption } = req.body;

        if (!phone || !file_path) {
            return res.status(400).json({ error: 'Phone and file_path are required' });
        }

        await whatsappClient.sendDocument(phone, file_path, caption || '');
        res.json({ success: true });
    } catch (error) {
        console.error('[Server] Error sending document:', error);
        res.status(500).json({ error: error.message });
    }
});

/**
 * Get client status.
 */
app.get('/status', (req, res) => {
    res.json({
        ready: whatsappClient.isReady,
        message_queue_size: messageQueue.length
    });
});

// Start server
const PORT = process.env.WHATSAPP_PORT || 3002;

app.listen(PORT, async () => {
    console.log(`[Server] WhatsApp bot server listening on port ${PORT}`);
    console.log('[Server] Initializing WhatsApp client...');
    await initializeWhatsApp();
});

// Graceful shutdown
process.on('SIGINT', async () => {
    console.log('[Server] Shutting down gracefully...');
    await whatsappClient.destroy();
    process.exit(0);
});

process.on('SIGTERM', async () => {
    console.log('[Server] Shutting down gracefully...');
    await whatsappClient.destroy();
    process.exit(0);
});
