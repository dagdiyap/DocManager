/**
 * WhatsApp Web client wrapper with resource optimization.
 * 
 * This module uses whatsapp-web.js with optimized Puppeteer settings
 * to minimize memory and CPU usage on the CA's desktop.
 */

const { Client, LocalAuth } = require('whatsapp-web.js');
const qrcode = require('qrcode-terminal');

class WhatsAppClient {
    constructor() {
        this.client = null;
        this.isReady = false;
        this.messageHandlers = [];
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.reconnecting = false;
    }

    /**
     * Initialize WhatsApp client with resource-optimized settings.
     */
    async initialize() {
        console.log('[WhatsApp] Initializing client with optimized settings...');

        this.client = new Client({
            authStrategy: new LocalAuth({
                dataPath: './.wwebjs_auth'
            }),
            puppeteer: {
                headless: true,
                args: [
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--single-process',
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--disable-translate',
                    '--disable-renderer-backgrounding',
                    '--disable-background-timer-throttling',
                    '--disable-backgrounding-occluded-windows',
                    '--metrics-recording-only',
                    '--mute-audio',
                    '--no-default-browser-check',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection',
                    '--js-flags=--max-old-space-size=256',
                    '--disable-component-update'
                ],
                defaultViewport: null
            },
            webVersionCache: {
                type: 'local'
            }
        });

        // QR Code event
        this.client.on('qr', (qr) => {
            console.log('[WhatsApp] QR Code received. Scan with your phone:');
            qrcode.generate(qr, { small: true });
        });

        // Ready event
        this.client.on('ready', () => {
            console.log('[WhatsApp] Client is ready!');
            this.isReady = true;
        });

        // Authenticated event
        this.client.on('authenticated', () => {
            console.log('[WhatsApp] Authentication successful!');
        });

        // Auth failure event
        this.client.on('auth_failure', (msg) => {
            console.error('[WhatsApp] Authentication failed:', msg);
        });

        // Disconnected event — auto-reconnect
        this.client.on('disconnected', async (reason) => {
            console.log('[WhatsApp] Client disconnected:', reason);
            this.isReady = false;
            await this._reconnect();
        });

        // Message event
        this.client.on('message', async (message) => {
            await this.handleIncomingMessage(message);
        });

        // Initialize client
        await this.client.initialize();
    }

    /**
     * Register a message handler callback.
     */
    onMessage(callback) {
        this.messageHandlers.push(callback);
    }

    /**
     * Handle incoming message and route to registered handlers.
     */
    async handleIncomingMessage(message) {
        try {
            // Skip status updates
            if (message.from === 'status@broadcast') return;

            // Keep full chat ID for group filtering in server.js
            const msgData = {
                from: message.from,
                body: message.body || '',
                hasMedia: message.hasMedia,
                type: message.type,
                timestamp: message.timestamp,
                id: message.id ? message.id._serialized : `msg_${Date.now()}`
            };

            // Call all registered handlers
            for (const handler of this.messageHandlers) {
                await handler(msgData, message);
            }
        } catch (error) {
            console.error('[WhatsApp] Error handling message:', error);
        }
    }

    /**
     * Send text message to a phone number.
     */
    async sendMessage(phone, text) {
        if (!this.isReady) {
            throw new Error('WhatsApp client is not ready');
        }

        try {
            // Format phone number with country code
            const chatId = phone.includes('@') ? phone : `${phone}@c.us`;
            await this.client.sendMessage(chatId, text);
            console.log(`[WhatsApp] Message sent to ${phone}`);
        } catch (error) {
            console.error(`[WhatsApp] Error sending message to ${phone}:`, error);
            throw error;
        }
    }

    /**
     * Send document file to a phone number.
     */
    async sendDocument(phone, filePath, caption = '') {
        if (!this.isReady) {
            throw new Error('WhatsApp client is not ready');
        }

        try {
            const MessageMedia = require('whatsapp-web.js').MessageMedia;
            const media = MessageMedia.fromFilePath(filePath);
            
            const chatId = phone.includes('@') ? phone : `${phone}@c.us`;
            await this.client.sendMessage(chatId, media, { caption });
            console.log(`[WhatsApp] Document sent to ${phone}: ${filePath}`);
        } catch (error) {
            console.error(`[WhatsApp] Error sending document to ${phone}:`, error);
            throw error;
        }
    }

    /**
     * Download media from a message.
     */
    async downloadMedia(message) {
        try {
            if (!message.hasMedia) {
                return null;
            }

            const media = await message.downloadMedia();
            return {
                data: Buffer.from(media.data, 'base64'),
                mimetype: media.mimetype,
                filename: media.filename || 'file'
            };
        } catch (error) {
            console.error('[WhatsApp] Error downloading media:', error);
            throw error;
        }
    }

    /**
     * Auto-reconnect with exponential backoff.
     */
    async _reconnect() {
        if (this.reconnecting) return;
        this.reconnecting = true;

        while (this.reconnectAttempts < this.maxReconnectAttempts && !this.isReady) {
            this.reconnectAttempts++;
            const delay = Math.min(5000 * this.reconnectAttempts, 60000);
            console.log(`[WhatsApp] Reconnecting in ${delay / 1000}s (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})...`);
            await new Promise(r => setTimeout(r, delay));

            try {
                await this.client.destroy().catch(() => {});
                this.client = null;
                await this.initialize();
                this.reconnectAttempts = 0;
                console.log('[WhatsApp] Reconnected successfully');
                break;
            } catch (error) {
                console.error(`[WhatsApp] Reconnect attempt ${this.reconnectAttempts} failed:`, error.message);
            }
        }

        if (!this.isReady && this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('[WhatsApp] Max reconnect attempts reached. Manual restart required.');
        }
        this.reconnecting = false;
    }

    /**
     * Destroy client and cleanup resources.
     */
    async destroy() {
        if (this.client) {
            await this.client.destroy();
            this.isReady = false;
            console.log('[WhatsApp] Client destroyed');
        }
    }
}

module.exports = WhatsAppClient;
