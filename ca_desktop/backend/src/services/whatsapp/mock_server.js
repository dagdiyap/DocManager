const express = require('express');
const bodyParser = require('body-parser');

const app = express();
app.use(bodyParser.json());

const messages = [];

app.get('/health', (req, res) => {
    res.json({ status: 'ok', whatsapp_ready: true, mode: 'MOCK' });
});

app.post('/send-message', (req, res) => {
    const { phone, message } = req.body;
    console.log(`\n📤 BOT → ${phone}:`);
    console.log(`   ${message.split('\n').join('\n   ')}`);
    messages.push({ direction: 'outbound', phone, message, timestamp: Date.now() });
    res.json({ success: true });
});

app.post('/send-document', (req, res) => {
    const { phone, file_path, caption } = req.body;
    console.log(`\n📎 BOT → ${phone}: Sending document`);
    console.log(`   File: ${file_path}`);
    if (caption) console.log(`   Caption: ${caption}`);
    messages.push({ direction: 'outbound', phone, type: 'document', file_path, timestamp: Date.now() });
    res.json({ success: true });
});

app.get('/status', (req, res) => {
    res.json({ ready: true, message_count: messages.length });
});

app.get('/messages', (req, res) => {
    res.json({ messages });
});

const PORT = 3002;
app.listen(PORT, () => {
    console.log('='.repeat(60));
    console.log('WhatsApp Mock Server - Running on port', PORT);
    console.log('='.repeat(60));
    console.log('This simulates WhatsApp responses without real connection.');
    console.log('All bot messages will be printed here.\n');
});
