# 📧 Quick Email Setup Guide

**You're not receiving emails because the Resend API key is not configured.**

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Get Free Resend API Key

1. **Go to**: https://resend.com
2. **Sign up** (free account - 3,000 emails/month)
3. **Login** and go to: https://resend.com/api-keys
4. **Click** "Create API Key"
5. **Copy** the key (starts with `re_`)

### Step 2: Add to DocManager

1. **Open terminal** in DocManager folder:
   ```bash
   cd /Users/pdagdiya/DocManager
   ```

2. **Edit .env file**:
   ```bash
   nano .env
   ```

3. **Add this line**:
   ```
   RESEND_API_KEY=re_paste_your_key_here
   ```

4. **Save**: Press `Ctrl+X`, then `Y`, then `Enter`

### Step 3: Restart DocManager

```bash
# Stop current servers (Ctrl+C in terminal)
# Then restart
./start.sh
```

### Step 4: Test Email

1. **Login**: http://localhost:5174/ca
2. **Go to**: Reminders
3. **Create reminder** with:
   - Select 1 client
   - Add document name
   - **Check "Email" box** ✓
   - Uncheck "WhatsApp"
   - Submit

4. **Check**: Client's email inbox (and spam folder)

---

## ✅ What You Get

- ✅ **3,000 free emails per month**
- ✅ **Professional email delivery**
- ✅ **No credit card required**
- ✅ **Works immediately**

---

## ❌ Why Emails Aren't Working Now

**Current Status**: No `RESEND_API_KEY` in `.env` file

**Fix**: Follow steps above to add API key

**After fix**: Emails will be sent automatically when you create reminders with "Email" option checked

---

## 🔍 Verify Setup

Check if API key is loaded:

```bash
# Check .env file
cat .env | grep RESEND_API_KEY

# Should show:
# RESEND_API_KEY=re_xxxxxx...
```

---

## 📚 Detailed Guide

For complete documentation, see: `docs/guides/EMAIL_SETUP.md`

---

## 🆘 Troubleshooting

**"Still not working"**:
1. Make sure you restarted DocManager after adding API key
2. Check client has email address in their profile
3. Check spam folder
4. Verify API key is correct (no extra spaces)

**"Invalid API key"**:
- Go back to https://resend.com/api-keys
- Create new key
- Update `.env` file
- Restart DocManager

---

**That's it!** Once you add the API key and restart, emails will work automatically.
