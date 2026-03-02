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
                    '--disable-gpu',
                    '--disable-software-rasterizer',
                    '--disable-extensions',
                    '--disable-background-networking',
                    '--disable-default-apps',
                    '--disable-sync',
                    '--metrics-recording-only',
                    '--mute-audio',
                    '--no-default-browser-check',
                    '--disable-features=TranslateUI',
                    '--disable-ipc-flooding-protection'
                ],
                defaultViewport: {
                    width: 800,
                    height: 600
                }
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

        // Disconnected event
        this.client.on('disconnected', (reason) => {
            console.log('[WhatsApp] Client disconnected:', reason);
            this.isReady = false;
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
            // Extract phone number (remove @c.us suffix)
            const phone = message.from.replace('@c.us', '');
            
            // Create message object
            const msgData = {
                from: phone,
                body: message.body,
                hasMedia: message.hasMedia,
                type: message.type,
                timestamp: message.timestamp,
                id: message.id._serialized
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
