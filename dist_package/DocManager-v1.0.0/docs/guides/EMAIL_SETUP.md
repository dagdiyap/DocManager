# Email Configuration Guide

**Setting up Email Reminders in DocManager**

---

## Overview

DocManager uses **Resend** (https://resend.com) to send email reminders to clients. This guide explains how to configure email functionality.

---

## Why Resend?

✅ **Professional email delivery**  
✅ **Simple API** - Easy integration  
✅ **Free tier available** - 3,000 emails/month free  
✅ **Reliable delivery** - High deliverability rates  
✅ **No SMTP configuration** - Just API key needed

---

## Step-by-Step Setup

### 1. Create Resend Account

1. Visit https://resend.com
2. Click "Sign Up" (top right)
3. Enter your email and create password
4. Verify your email address

### 2. Get API Key

1. **Login to Resend Dashboard**: https://resend.com/overview
2. **Navigate to API Keys**:
   - Click "API Keys" in left sidebar
   - Or visit: https://resend.com/api-keys

3. **Create New API Key**:
   - Click "Create API Key" button
   - Name: `DocManager-Production` (or any name you prefer)
   - Permission: Select "Sending access"
   - Click "Create"

4. **Copy API Key**:
   - **IMPORTANT**: Copy the key immediately (shown only once!)
   - Format: `re_xxxxxxxxxxxxxxxxxxxxxxxxxx`
   - Store securely - you won't see it again

### 3. Add API Key to DocManager

#### Option A: Using .env File (Recommended)

1. **Open/Create `.env` file** in project root:
   ```bash
   cd /path/to/DocManager
   nano .env
   ```

2. **Add this line**:
   ```bash
   RESEND_API_KEY=re_your_actual_api_key_here
   ```

3. **Save and close**:
   - Press `Ctrl+X`, then `Y`, then `Enter`

4. **Verify file permissions** (security):
   ```bash
   chmod 600 .env
   ```

#### Option B: Environment Variable

```bash
# macOS/Linux - Add to ~/.bashrc or ~/.zshrc
export RESEND_API_KEY=re_your_actual_api_key_here

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

### 4. Verify Domain (For Production)

**For Testing**: Skip this step - use Resend's test mode

**For Production**:

1. **Add Your Domain** in Resend Dashboard:
   - Go to "Domains" section
   - Click "Add Domain"
   - Enter your domain (e.g., `dagdiyaassociates.com`)

2. **Add DNS Records**:
   - Resend will show DNS records to add
   - Add these to your domain's DNS settings
   - Records include: SPF, DKIM, DMARC

3. **Verify Domain**:
   - Click "Verify" in Resend dashboard
   - Wait for verification (can take up to 48 hours)

4. **Set From Email**:
   - Once verified, emails can be sent from `contact@yourdomain.com`
   - Until then, use `onboarding@resend.dev` (testing only)

---

## Testing Email Configuration

### Quick Test

```bash
# Start DocManager
./start.sh

# Wait for servers to start, then test
curl -X POST "http://localhost:8443/api/v1/reminders/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_phones": ["9876543210"],
    "document_names": ["Test Email"],
    "document_types": ["ITR"],
    "send_via_email": true,
    "send_via_whatsapp": false
  }'
```

### In DocManager UI

1. **Login to CA Dashboard**: http://localhost:5174/ca
2. **Go to Reminders**
3. **Create New Reminder**:
   - Select a client
   - Add document name and type
   - **Check "Email" option**
   - Uncheck "WhatsApp"
   - Submit

4. **Check Result**:
   - Should see success message: "X emails sent"
   - Check client's email inbox
   - Also check spam folder

### Check Logs

```bash
# View backend logs
tail -f logs/backend.log

# Look for email-related messages
grep "email" logs/backend.log
```

---

## Troubleshooting

### ❌ "Email not sending"

**Check 1: API Key Set?**
```bash
# Check if API key is in .env
cat .env | grep RESEND_API_KEY

# Should show:
# RESEND_API_KEY=re_xxxxxx...
```

**Check 2: Backend Loaded Key?**
```bash
# Check backend logs
tail -f logs/backend.log

# Restart backend to reload .env
pkill -f uvicorn
./start.sh
```

**Check 3: Valid API Key?**
```bash
# Test API key directly
curl https://api.resend.com/emails \
  -H "Authorization: Bearer re_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "from": "onboarding@resend.dev",
    "to": "your-email@example.com",
    "subject": "Test",
    "html": "<p>Test email</p>"
  }'

# Should return: {"id": "xxx"} if valid
# Should return: error if invalid
```

**Check 4: Client Has Email?**
- Go to Clients section
- Check client has valid email address
- Update if needed

### ❌ "401 Unauthorized" from Resend

**Problem**: Invalid or expired API key

**Solution**:
1. Go to Resend dashboard
2. Create new API key
3. Update `.env` file
4. Restart DocManager

### ❌ Emails Going to Spam

**Problem**: Domain not verified or using onboarding@resend.dev

**Solutions**:
1. **Short term**: Ask clients to check spam and mark as "Not Spam"
2. **Long term**: 
   - Verify your domain in Resend
   - Use professional from address (contact@yourdomain.com)
   - Add SPF, DKIM, DMARC records

### ❌ "Rate limit exceeded"

**Problem**: Free tier limit reached (3,000/month)

**Solutions**:
1. **Check usage** in Resend dashboard
2. **Upgrade plan** if needed:
   - Pro: $20/month for 50,000 emails
   - Business: Custom pricing
3. **Wait until next month** for free tier reset

### ❌ Email format looks wrong

**Problem**: HTML template issue

**Check**:
```bash
# View email template
cat ca_desktop/backend/src/services/reminder_service.py

# Search for email HTML
grep -A 20 "html_content" ca_desktop/backend/src/services/reminder_service.py
```

---

## Email Template Customization

### Current Template

Location: `ca_desktop/backend/src/services/reminder_service.py`

```python
html_content = f"""
<html>
<body style="font-family: Arial, sans-serif;">
    <h2>Document Reminder</h2>
    <p>Dear {client.name},</p>
    <p>This is a reminder regarding the following document(s):</p>
    ...
</body>
</html>
"""
```

### Customize Template

1. **Open file**:
   ```bash
   nano ca_desktop/backend/src/services/reminder_service.py
   ```

2. **Find `html_content` variable**

3. **Modify HTML** as needed:
   - Change colors
   - Add logo
   - Update text
   - Add footer

4. **Save and restart** backend

---

## Production Best Practices

### Security
- ✅ Never commit API key to git
- ✅ Use `.env` file (in `.gitignore`)
- ✅ Restrict file permissions: `chmod 600 .env`
- ✅ Rotate API keys periodically

### Reliability
- ✅ Verify your domain
- ✅ Monitor email deliverability in Resend dashboard
- ✅ Keep backup of API key securely
- ✅ Set up email failure logging

### Compliance
- ✅ Include unsubscribe link (if sending marketing)
- ✅ Add physical address in footer
- ✅ Follow CAN-SPAM Act (if in US)
- ✅ GDPR compliance (if EU clients)

---

## Free Tier Limits

**Resend Free Tier**:
- **3,000 emails/month**
- **100 emails/day**
- **Domain verification**: 1 domain
- **API access**: Full access

**Usage Calculation**:
- 5 clients × 2 documents × 1 email = 10 emails
- 100 clients × 2 documents = 200 emails
- Average CA: ~500-1,000 emails/month
- **Free tier is sufficient for most CAs**

---

## Paid Plans (If Needed)

### Pro Plan - $20/month
- 50,000 emails/month
- Unlimited domains
- Priority support
- 99.9% uptime SLA

### When to Upgrade?
- 200+ active clients
- Sending frequent reminders (weekly)
- Multiple CAs using same instance
- Need guaranteed delivery

---

## Alternative: Using Your Own SMTP

If you prefer to use your own email server instead of Resend:

### Gmail SMTP (Not Recommended for Production)
```bash
# In .env
EMAIL_PROVIDER=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### Professional Email Service
- **Google Workspace**: Business email
- **Microsoft 365**: Business email
- **Custom SMTP**: Your email server

**Note**: Requires code changes to support SMTP. Resend is simpler and more reliable.

---

## FAQ

**Q: Do I need to pay for Resend?**  
A: No, free tier (3,000 emails/month) is sufficient for most CAs.

**Q: Can I use Gmail to send emails?**  
A: Not recommended. Gmail limits sending and may mark as spam. Use Resend.

**Q: What happens if I exceed free tier?**  
A: Emails will be queued or rejected. Upgrade to Pro plan.

**Q: Can multiple CAs share one API key?**  
A: Yes, but all emails count toward same limit. Consider separate accounts for high volume.

**Q: Is Resend secure?**  
A: Yes, Resend uses industry-standard security (TLS encryption, secure API).

**Q: What if Resend is down?**  
A: Rare, but emails will be queued and sent when service resumes. Check status: https://resend.com/status

**Q: Can I send attachments?**  
A: Yes, Resend supports attachments. See Resend docs for details.

---

## Support

### Resend Support
- **Documentation**: https://resend.com/docs
- **API Reference**: https://resend.com/docs/api-reference
- **Status Page**: https://resend.com/status
- **Support Email**: support@resend.com

### DocManager Support
- Check `docs/guides/USER_GUIDE.md`
- Review `logs/backend.log`
- Check this guide's troubleshooting section

---

## Quick Checklist

Before sending your first email:

- [ ] Created Resend account
- [ ] Got API key from dashboard
- [ ] Added `RESEND_API_KEY` to `.env` file
- [ ] Restarted DocManager (`./start.sh`)
- [ ] Client has valid email address
- [ ] Tested sending a reminder
- [ ] Checked client's email inbox (and spam)
- [ ] Verified email delivered successfully

---

**You're all set!** Your DocManager can now send professional email reminders to clients.

For production use, consider verifying your domain for better deliverability.
