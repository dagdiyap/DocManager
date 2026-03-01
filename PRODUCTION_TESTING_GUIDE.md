# Production Testing Guide - CA Lokesh Dagdiya

## ✅ Environment Status

**All systems running and ready for testing!**

- ✅ Backend: Running on 0.0.0.0:8443 with external access
- ✅ Cloudflare Tunnel: Active and exposing backend to internet
- ✅ Database: CA Lokesh + Test Client + 4 Documents configured
- ✅ Standalone Website: Deployed to Vercel (auto-deploying latest changes)

---

## 🌐 URLs for Testing

### Cloudflare Tunnel URL (Backend API)
```
https://unfortunately-metabolism-residents-nokia.trycloudflare.com
```
**⚠️ Note:** This URL changes every time you restart the tunnel. Current session only.

### Standalone Website (Vercel)
```
https://ca-lokesh-dagdiya.vercel.app/
```
**Status:** Auto-deploying from latest GitHub push (should be live in ~1 minute)

### Client Portal Login
```
https://unfortunately-metabolism-residents-nokia.trycloudflare.com/portal/login
```

---

## 👤 Test Credentials

### CA Admin Login
- **Username:** `lokesh`
- **Password:** `admin123`
- **Login URL:** `{tunnel_url}/ca/login`

### Test Client Login
- **Phone:** `9876543210`
- **Password:** `test123`
- **Name:** Amit Sharma
- **Login URL:** `{tunnel_url}/portal/login`

---

## 📱 WhatsApp Share URL

**Copy and send this URL to test on mobile:**

```
https://wa.me/?text=Hi!%20Access%20your%20documents%20at%20Dagdiya%20Associates%20client%20portal.%0A%0ALogin%20Details:%0APhone:%209876543210%0APassword:%20test123%0A%0APortal:%20https://unfortunately-metabolism-residents-nokia.trycloudflare.com/portal/login
```

**What this does:**
- Opens WhatsApp with pre-filled message
- Contains client credentials and portal link
- Client can click link and login directly on mobile

---

## 📄 Test Documents Available

Client `9876543210` has **4 documents** for testing:

### 2024 Documents
1. **ITR_2024.txt** - Income Tax Return FY 2023-24
2. **GST_Returns_Q1.txt** - GST Returns Q1 2024

### 2023 Documents
3. **ITR_2023.txt** - Income Tax Return FY 2022-23
4. **Audit_Report.txt** - Tax Audit Report FY 2022-23

**Location:** `/Users/pdagdiya/DocManager/documents/9876543210/`

---

## 🧪 Testing Checklist

### Desktop Browser Testing
- [ ] Open standalone website: `https://ca-lokesh-dagdiya.vercel.app/`
- [ ] Verify DAGDIYA ASSOCIATES heading, moving banner, services, testimonials
- [ ] Test client portal login at tunnel URL
- [ ] Login with phone `9876543210` and password `test123`
- [ ] Verify 4 documents are visible in portal
- [ ] Test document download (click on any document)

### Mobile Browser Testing (Android Chrome)
- [ ] Click WhatsApp share URL on desktop
- [ ] Send message to yourself on WhatsApp
- [ ] Open WhatsApp on Android phone
- [ ] Click the portal link in WhatsApp message
- [ ] Login with credentials from message
- [ ] Verify documents load on mobile
- [ ] Test document download on mobile
- [ ] Verify download works (file should download to phone)

### Mobile Browser Testing (iOS Safari)
- [ ] Repeat above steps on iPhone
- [ ] Verify portal works on Safari
- [ ] Test document download on iOS
- [ ] Verify file opens/downloads correctly

---

## 🔧 API Endpoints (for debugging)

### Public Endpoints (no auth required)
```bash
# CA Profile
GET {tunnel_url}/api/v1/public/ca-slug/lokesh-dagdiya

# Portal Metadata
GET {tunnel_url}/api/v1/public/ca-slug/lokesh-dagdiya/portal
```

### Authenticated Endpoints
```bash
# Login
POST {tunnel_url}/api/v1/auth/login
Content-Type: application/x-www-form-urlencoded
Body: username=9876543210&password=test123

# Get Documents (requires Bearer token from login)
GET {tunnel_url}/api/v1/documents/
Authorization: Bearer {token}
```

---

## 📊 Resource Usage

**Current system load:**
- Backend: ~150MB RAM, <1% CPU
- Cloudflare Tunnel: ~40MB RAM, <1% CPU
- **Total:** ~190MB RAM, minimal CPU impact

**Acceptable for production use on CA's laptop.**

---

## ⚠️ Important Notes

### Tunnel URL Changes
- The Cloudflare Tunnel URL (`https://unfortunately-metabolism-residents-nokia.trycloudflare.com`) is **temporary**
- It changes every time you restart the tunnel
- For **persistent URL**, create a free Cloudflare account and use a named tunnel

### Email Service
- Email service (Resend) is configured but **API key not set**
- To enable email invites, set `RESEND_API_KEY` in `.env` file
- Without it, client invites work but emails won't be sent

### Document Downloads on Mobile
- Downloads should work on both Android and iOS
- Android: Files download to Downloads folder
- iOS: Files open in Safari viewer, can be saved to Files app
- Test with actual mobile devices to verify

---

## 🚀 How to Restart Everything

If you need to restart the backend and tunnel:

```bash
# Stop everything
pkill -f "uvicorn|cloudflared"

# Start backend
cd ca_desktop/backend
source venv/bin/activate
EXTERNAL_ACCESS=true EXTRA_CORS_ORIGINS="https://*.vercel.app,https://*.trycloudflare.com" \
  PYTHONPATH="$PWD/../..:$PYTHONPATH" \
  python -m uvicorn ca_desktop.backend.src.main:app --host 0.0.0.0 --port 8443 &

# Start Cloudflare Tunnel (in new terminal)
cloudflared tunnel --url http://localhost:8443

# New tunnel URL will be displayed - update WhatsApp message with new URL
```

---

## ✅ Success Criteria

**Complete end-to-end flow verified when:**
1. ✅ Standalone website loads on Vercel
2. ✅ Client can login via tunnel URL on mobile
3. ✅ Client sees all 4 documents in portal
4. ✅ Client can download documents on mobile (Android + iOS)
5. ✅ WhatsApp share URL works and opens portal correctly
6. ✅ No errors in browser console
7. ✅ Downloads work on both Android Chrome and iOS Safari

---

**Ready for real-world client testing!** 🎉

Send the WhatsApp URL to a test client and verify the complete flow works on their mobile device.
