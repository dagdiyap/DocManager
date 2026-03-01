# DocManager Demo Guide for CA Lokesh Dagdiya

## Quick Start Commands

### Option 1: Mac/Linux (Recommended for Demo)
```bash
cd /Users/pdagdiya/DocManager
./start.sh
```

### Option 2: Manual Start
```bash
# Terminal 1 - Backend
cd /Users/pdagdiya/DocManager/ca_desktop/backend
source venv/bin/activate
PYTHONPATH="$PWD/../..:$PYTHONPATH" uvicorn ca_desktop.backend.src.main:app --host 127.0.0.1 --port 8443

# Terminal 2 - Frontend
cd /Users/pdagdiya/DocManager/ca_desktop/frontend
npm run dev
```

**Access Points:**
- **Public Website**: http://localhost:5174/ca-lokesh-dagdiya
- **CA Dashboard**: http://localhost:5174/ca/login
- **Client Portal**: http://localhost:5174/ca-lokesh-dagdiya/login
- **API Docs**: http://localhost:8443/docs

---

## Demo Credentials

### CA Admin (Lokesh)
- **Username**: `lokesh`
- **Password**: `lokesh`
- **Dashboard**: http://localhost:5174/ca/login

### Sample Clients
- **Phone**: `9876543210` | **Password**: `client123`
- **Phone**: `9876543211` | **Password**: `client123`
- **Phone**: `9876543212` | **Password**: `client123`

---

## Complete Feature Walkthrough

### 1. Public CA Website (24/7 Shareable)
**URL**: http://localhost:5174/ca-lokesh-dagdiya

**Features to Show:**
- ✅ Professional hero section with Lokesh's photo
- ✅ About section with credentials (FCA, DISA, Forensic Audit)
- ✅ 4 Core services (GST, Bank Audits, Forensic, IS Audit)
- ✅ Industries served
- ✅ Client testimonials
- ✅ Contact information
- ✅ "Client Login" button → direct portal access

**Key Points:**
- This website runs 24/7 independently
- Can be hosted on Vercel for free
- Custom domain: `lokeshdagdiya.com` or `ca-lokesh-dagdiya.vercel.app`
- Fully responsive (mobile, tablet, desktop)

---

### 2. CA Dashboard Features

#### A. Client Management
**Navigate**: Dashboard → Clients

**Demo Flow:**
1. **Add New Client**
   - Click "Add Client" button
   - Fill: Name, Phone, Email, Client Type
   - System auto-generates secure password
   - **Invite Modal appears** with:
     - Portal URL
     - Username (phone)
     - Password
     - QR Code
     - WhatsApp share button
     - Copy-to-clipboard for all fields

2. **Bulk Client Upload**
   - Click "Bulk Upload" button
   - Upload Excel/Text file with phone numbers
   - System extracts phones (supports +91, 91, 10-digit)
   - Auto-creates clients with passwords
   - Download credentials CSV

3. **Client List View**
   - Search/filter clients
   - View compliance status
   - Edit client details
   - Delete clients

#### B. Document Management
**Navigate**: Dashboard → Documents

**Demo Flow:**
1. **Upload Documents**
   - Select client (phone number)
   - Choose year (2024, 2023, etc.)
   - Select document type
   - Upload file (PDF, JPG, PNG, Excel, Word)
   - System auto-indexes with hash

2. **Document Scanner**
   - Click "Scan Documents" button
   - System scans `documents/` folder
   - Auto-indexes all files by phone/year/type
   - Shows scan results

3. **Search & Filter**
   - Search by filename
   - Filter by client
   - Filter by year
   - Filter by document type

4. **Download Documents**
   - Click download → generates secure token
   - Token expires in 10 minutes
   - One-time use only
   - Audit log tracks all downloads

#### C. Messaging & File Sharing
**Navigate**: Dashboard → Messages

**Demo Flow:**
1. **Send Message to Client**
   - Select client
   - Enter subject & message
   - Send → client sees in portal

2. **Share Files Manually**
   - Upload file for specific client
   - Add description
   - Client gets notified
   - Secure download with token

#### D. Reminders & Compliance
**Navigate**: Dashboard → Reminders

**Demo Flow:**
1. **Create Individual Reminder**
   - Select client
   - Choose type (document, compliance, custom)
   - Set date
   - Add message
   - Optional: recurring (yearly, quarterly, monthly)

2. **Send Group Reminders**
   - Filter: "Missing Documents" or "Compliance Rule"
   - Select document type (e.g., ITR, GST Return)
   - System finds all clients missing that document
   - Send bulk reminder

3. **Compliance Rules**
   - View predefined rules (Individual, Partnership, Company)
   - Check client compliance status
   - Auto-reminders for non-compliant clients

#### E. CA Profile & Website Management
**Navigate**: Dashboard → Profile

**Demo Flow:**
1. **Update Profile**
   - Firm name: "Lokesh Dagdiya & Associates"
   - Professional bio
   - Contact details
   - Upload logo

2. **Manage Services**
   - Add/edit/delete services
   - Reorder services
   - Set background images

3. **Manage Testimonials**
   - Add client testimonials
   - Set ratings (1-5 stars)
   - Reorder testimonials

4. **Upload Media**
   - Office photos
   - Team photos
   - Certificate images
   - Appears in public website gallery

---

### 3. Client Portal Features

**Login**: http://localhost:5174/ca-lokesh-dagdiya/login
- **Username**: `9876543210`
- **Password**: `client123`

**Features Clients See:**
1. **My Documents**
   - View all uploaded documents
   - Filter by year/type
   - Download with secure token
   - See upload date

2. **Messages**
   - Read messages from CA
   - View shared files
   - Download shared files

3. **Reminders**
   - See upcoming deadlines
   - View compliance requirements
   - Check document requests

4. **Profile**
   - View contact info
   - Update password
   - See account details

---

## Advanced Features

### 1. Audit Logging
**Navigate**: Dashboard → Audit Logs

**Tracks:**
- Client creation/updates/deletion
- Document uploads/downloads
- Login attempts (success/failure)
- Password changes
- Reminder creation
- Profile updates

**Fields Logged:**
- Action type
- User (CA or client)
- Timestamp
- IP address
- Details (what changed)

### 2. Security Features
- ✅ JWT authentication with expiry
- ✅ Bcrypt password hashing
- ✅ Secure download tokens (HMAC-signed, one-time use)
- ✅ Path traversal protection
- ✅ File type validation
- ✅ Rate limiting (60 req/min)
- ✅ Audit logging for all actions

### 3. Multi-Tenant Architecture
- Each CA gets unique slug: `ca-lokesh-dagdiya`
- Separate client portals per CA
- Isolated data per CA
- Custom branding per CA

---

## Hosting the Public Website (Free for 10 CAs)

### Option A: Static Export to Vercel (Recommended)

**Steps:**
1. Export CA profile data:
```bash
curl http://localhost:8443/api/v1/public/ca-slug/lokesh-dagdiya > lokesh-data.json
```

2. Build static site:
```bash
cd ca_desktop/frontend
npm run build
```

3. Deploy to Vercel:
```bash
npm install -g vercel
vercel --prod
```

**Result:**
- URL: `https://ca-lokesh-dagdiya.vercel.app`
- Custom domain: `lokeshdagdiya.com` (configure in Vercel)
- Free SSL certificate
- Global CDN
- Auto-deploy on git push

### Option B: Keep Backend Running 24/7

**Use Railway.app (Free Tier):**
1. Push code to GitHub
2. Connect Railway to repo
3. Deploy backend
4. Deploy frontend
5. Configure environment variables

**Limits:**
- 500 hours/month free
- $5/month for unlimited

---

## Demo Script for CA Call

### Opening (2 minutes)
"Hi Lokesh! Let me show you DocManager - a complete document management system I've built specifically for CAs like you."

### Public Website Demo (3 minutes)
1. Open: http://localhost:5174/ca-lokesh-dagdiya
2. Show:
   - "This is YOUR public website with your photo and credentials"
   - "Clients can access their portal 24/7 from here"
   - "We can host this for free on Vercel"
   - "You can have custom domain: lokeshdagdiya.com"

### Client Onboarding Demo (5 minutes)
1. Login to CA dashboard
2. Add new client:
   - "Watch how easy it is to onboard a client"
   - Show auto-generated password
   - Show invite modal with QR code
   - "You can WhatsApp this directly to the client"
3. Bulk upload:
   - "Have 50 clients? Upload Excel file"
   - "System creates all accounts and passwords"

### Document Management Demo (5 minutes)
1. Upload document:
   - "Upload any file - PDF, Excel, images"
   - "System organizes by client/year/type"
2. Show scanner:
   - "Already have documents in folders? Scan them"
3. Show client portal:
   - "This is what your client sees"
   - "They can download their documents anytime"

### Compliance & Reminders Demo (3 minutes)
1. Create reminder
2. Send group reminder:
   - "Find all clients missing ITR"
   - "Send reminder to all at once"

### Security & Audit Demo (2 minutes)
1. Show audit logs:
   - "Every action is logged"
   - "See who downloaded what, when"
2. Show secure downloads:
   - "Tokens expire in 10 minutes"
   - "One-time use only"

### Closing (2 minutes)
"Questions? The system is ready to use today. We can host your website live in 10 minutes."

---

## Troubleshooting

### Backend won't start
```bash
# Check if port 8443 is in use
lsof -i :8443
kill -9 <PID>

# Restart
cd ca_desktop/backend
source venv/bin/activate
uvicorn ca_desktop.backend.src.main:app --host 127.0.0.1 --port 8443
```

### Frontend won't start
```bash
# Check if port 5174 is in use
lsof -i :5174
kill -9 <PID>

# Restart
cd ca_desktop/frontend
npm run dev
```

### Database issues
```bash
# Reset database
cd /Users/pdagdiya/DocManager
rm ca_desktop.db
python scripts/setup_database.py
```

---

## Next Steps After Demo

1. **Decide on hosting strategy**
   - Static site on Vercel (free, easy)
   - Full stack on Railway (free tier, 500hrs/month)

2. **Get custom domain**
   - Register `lokeshdagdiya.com` (~$10/year)
   - Point to Vercel/Railway

3. **Customize branding**
   - Upload logo
   - Add more services
   - Add testimonials
   - Upload office photos

4. **Onboard real clients**
   - Bulk upload existing clients
   - Send WhatsApp invites
   - Upload their documents

5. **Set up compliance rules**
   - Define document requirements
   - Set up recurring reminders

---

## Support & Documentation

- **Full Documentation**: `/Users/pdagdiya/DocManager/docs/`
- **API Documentation**: http://localhost:8443/docs
- **Test Reports**: `/Users/pdagdiya/DocManager/COMPREHENSIVE_TEST_REPORT.md`
- **All Tests Passing**: 22 API tests + 24 cross-platform tests

---

**Ready to go live? Let's deploy Lokesh's website now!**
