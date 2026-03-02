/**
 * WhatsApp bot server - Bridge between Node.js WhatsApp client and Python backend.
 * 
 * This server runs the WhatsApp Web client and exposes a simple HTTP API
 * for the Python backend to send/receive messages.
 */

const express = require('express');
const bodyParser = require('body-parser');
const fs = require('fs');
const path = require('path');
const WhatsAppClient = require('./client');

const app = express();
app.use(bodyParser.json());

const whatsappClient = new WhatsAppClient();
let pythonBackendUrl = process.env.BACKEND_URL || 'http://localhost:8443';

// Only process messages received AFTER server starts
const serverStartTime = Math.floor(Date.now() / 1000);

/**
 * Retry a function up to 3 times with backoff.
 */
async function forwardWithRetry(fn, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            return await fn();
        } catch (error) {
            if (attempt === maxRetries) {
                console.error(`[Server] All ${maxRetries} retry attempts failed:`, error.message);
                throw error;
            }
            const delay = 1000 * attempt;
            console.warn(`[Server] Attempt ${attempt} failed, retrying in ${delay}ms...`);
            await new Promise(r => setTimeout(r, delay));
        }
    }
}

/**
 * Initialize WhatsApp client on server start.
 */
async function initializeWhatsApp() {
    try {
        await whatsappClient.initialize();
        
        // Register message handler to forward to Python backend
        whatsappClient.onMessage(async (msgData, rawMessage) => {
            try {
                // Skip old messages from before server started
                if (msgData.timestamp && msgData.timestamp < serverStartTime) {
                    return;
                }

                // Skip group messages
                if (msgData.from.includes('@g.us') || msgData.from.includes('@broadcast')) {
                    return;
                }

                console.log(`[Server] Incoming message from ${msgData.from}: ${msgData.body?.substring(0, 50)}`);

                // Forward message to Python backend with retry
                await forwardWithRetry(async () => {
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
                        throw new Error(`Backend responded ${response.status}: ${response.statusText}`);
                    }
                });

                // If message has media, download and forward
                if (msgData.hasMedia) {
                    const media = await whatsappClient.downloadMedia(rawMessage);
                    if (media) {
                        // Save to temp file, then upload via multipart
                        const tmpFile = path.join('/tmp', `wa_upload_${Date.now()}_${media.filename}`);
                        fs.writeFileSync(tmpFile, media.data);

                        try {
                            const boundary = '----WABotBoundary' + Date.now();
                            const filename = media.filename || 'file';
                            const parts = [
                                `--${boundary}\r\nContent-Disposition: form-data; name="phone"\r\n\r\n${msgData.from}`,
                                `--${boundary}\r\nContent-Disposition: form-data; name="mimetype"\r\n\r\n${media.mimetype}`,
                                `--${boundary}\r\nContent-Disposition: form-data; name="file"; filename="${filename}"\r\nContent-Type: ${media.mimetype}\r\n\r\n`,
                            ];
                            const header = Buffer.from(parts.join('\r\n') + '\r\n');
                            const footer = Buffer.from(`\r\n--${boundary}--\r\n`);
                            const body = Buffer.concat([header, media.data, footer]);

                            await fetch(`${pythonBackendUrl}/api/v1/whatsapp/upload`, {
                                method: 'POST',
                                headers: { 'Content-Type': `multipart/form-data; boundary=${boundary}` },
                                body: body
                            });
                        } finally {
                            fs.unlinkSync(tmpFile);
                        }
                    }
                }
            } catch (error) {
                console.error('[Server] Error processing incoming message:', error.message);
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
        ready: whatsappClient.isReady
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

process.on('unhandledRejection', (reason, promise) => {
    console.error('[Server] Unhandled Promise Rejection:', reason);
});

process.on('uncaughtException', (error) => {
    console.error('[Server] Uncaught Exception:', error);
});
