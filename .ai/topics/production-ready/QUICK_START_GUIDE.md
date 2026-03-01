# DocManager - Quick Start Guide for CA Lokesh Dagdiya

**Goal**: Get your professional website running locally, update your details, and see it live.

---

## 📋 Prerequisites

Make sure you have installed:
- ✅ Python 3.9+ 
- ✅ Node.js 18+
- ✅ Git

---

## 🚀 Step-by-Step Setup (Local Testing)

### **Step 1: Install Backend Dependencies**

```bash
# Navigate to backend directory
cd /Users/pdagdiya/DocManager/ca_desktop/backend

# Install Python packages
pip install -r requirements.txt
```

**Expected output**: All packages install successfully (openpyxl, pandas, resend, qrcode, etc.)

---

### **Step 2: Initialize Database**

```bash
# Still in backend directory
# Run database migrations
alembic upgrade head
```

**Expected output**: Database created at `ca_desktop.db`

---

### **Step 3: Create Your CA Account**

```bash
# Start Python shell
python

# Then run these commands:
```

```python
from src.database import SessionLocal
from src.models import User, CAProfile
from src.dependencies import get_password_hash

db = SessionLocal()

# Create your CA user
ca_user = User(
    username="lokesh",
    email="lokesh@dagdiyaassociates.com",
    password_hash=get_password_hash("Lokesh@2024"),  # Change this password!
    display_name="CA Lokesh Dagdiya",
    slug="lokesh-dagdiya",
)
db.add(ca_user)
db.commit()
db.refresh(ca_user)

# Create your CA profile
ca_profile = CAProfile(
    ca_id=ca_user.id,
    firm_name="Lokesh Dagdiya & Associates",
    professional_bio="""CA Lokesh Dagdiya is a Fellow Chartered Accountant from ICAI with DISA and certifications in Concurrent Audit and Forensic Audit. He specializes in GST compliances, consultancy and litigation, along with comprehensive bank audits including statutory, forensic, concurrent audits, and due diligence reviews. Currently serving as Treasurer of Nanded Branch of WIRC of ICAI.""",
    address="Nanded, Maharashtra, India",
    phone_number="+91 98765 43210",  # Update with your real number
    email="lokesh@dagdiyaassociates.com",
    website_url="https://dagdiyaassociates.com",
)
db.add(ca_profile)
db.commit()

print(f"✅ Created CA user: {ca_user.username}")
print(f"✅ Your slug: {ca_user.slug}")
print(f"✅ Login at: http://localhost:5173/ca/login")
print(f"✅ Website at: http://localhost:5173/ca-lokesh-dagdiya")

# Exit Python shell
exit()
```

---

### **Step 4: Start Backend Server**

```bash
# Still in backend directory
uvicorn src.main:app --reload --port 8443
```

**Expected output**: 
```
INFO:     Uvicorn running on http://127.0.0.1:8443
INFO:     Application startup complete.
```

**Keep this terminal running!**

---

### **Step 5: Start Frontend (New Terminal)**

```bash
# Open NEW terminal window
cd /Users/pdagdiya/DocManager/ca_desktop/frontend

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

**Expected output**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

**Keep this terminal running too!**

---

## 🎯 Step 6: Login and Update Your Profile

### **A. Login to CA Dashboard**

1. Open browser: `http://localhost:5173/ca/login`
2. Enter credentials:
   - **Username**: `lokesh`
   - **Password**: `Lokesh@2024` (or what you set)
3. Click **Login**

You should see the CA Dashboard!

---

### **B. Update Your Profile**

1. Click **"Profile & Website"** in the left sidebar
2. You'll see 4 tabs:

#### **Tab 1: Basic Info**
Update these fields:
- ✏️ **Firm Name**: Lokesh Dagdiya & Associates
- ✏️ **Email**: Your real email
- ✏️ **Phone**: Your real phone number
- ✏️ **Address**: Your office address
- ✏️ **Professional Bio**: Copy from LOKESH_DAGDIYA_CONTENT.md
- ✏️ **Website URL**: Your website (if any)
- ✏️ **LinkedIn URL**: Your LinkedIn profile

Click **"Save Changes"** button

---

#### **Tab 2: Media Gallery**
Upload 5-10 photos:
- Office exterior
- Office interior
- Team photos
- Professional headshot
- Certificates/Awards

**How to upload**:
1. Click **"Upload Image"** button
2. Select image file (JPG/PNG)
3. Repeat for each photo
4. Photos appear in grid automatically

---

#### **Tab 3: Services**
Add your 4 main services:

**Service 1:**
- Title: `GST Compliances & Litigation`
- Description: `Comprehensive GST services including compliances, consultancy, litigation support, and representation before authorities.`
- Click **"Add Service"**

**Service 2:**
- Title: `Bank Audits (Specialized)`
- Description: `Statutory, forensic, concurrent audits, due diligence reviews, and stock & debtor audits for banking sector.`
- Click **"Add Service"**

**Service 3:**
- Title: `Forensic Audit & Fraud Detection`
- Description: `Certified forensic accounting, fraud investigation, and financial irregularity detection services.`
- Click **"Add Service"**

**Service 4:**
- Title: `Information System Audit`
- Description: `DISA-certified IT system audits, cybersecurity assessments, and IT compliance reviews.`
- Click **"Add Service"**

---

#### **Tab 4: Testimonials**
Add 2-3 client testimonials:

**Testimonial 1:**
- Client Name: `Amit Sharma`
- Content: `Lokesh has been handling our accounts for the past 5 years. His attention to detail and proactive tax planning has saved us lakhs in taxes. Highly recommended!`
- Rating: ⭐⭐⭐⭐⭐ (5 stars)
- Click **"Add Testimonial"**

**Testimonial 2:**
- Client Name: `Priya Patel`
- Content: `As a startup founder, I needed someone who understood both business and compliance. Lokesh provided invaluable guidance during our growth phase. Professional and reliable!`
- Rating: ⭐⭐⭐⭐⭐ (5 stars)
- Click **"Add Testimonial"**

---

## 🌐 Step 7: View Your Website

Open new browser tab: `http://localhost:5173/ca-lokesh-dagdiya`

**You should see**:
- ✅ Professional hero section with gradient background
- ✅ Your bio and firm name
- ✅ About section with your professional bio
- ✅ Photo gallery (if you uploaded photos)
- ✅ 4 service cards with hover effects
- ✅ Industries we serve section
- ✅ Client testimonials (if you added them)
- ✅ Contact section with your details
- ✅ "Client Login" button in top-right

---

## 🎨 Website Features You'll See

### **Responsive Design**
- ✅ Works on mobile, tablet, desktop
- ✅ Test by resizing browser window

### **Smooth Animations**
- ✅ Hover over service cards → They lift up and change color
- ✅ Hover over industry icons → They scale up
- ✅ Hover over photos → They zoom in
- ✅ Scroll down → Smooth transitions

### **Professional Elements**
- ✅ Gradient backgrounds (blue/indigo/purple)
- ✅ Animated blob shapes in hero
- ✅ Shadow effects on cards
- ✅ Rounded corners everywhere
- ✅ Professional color scheme
- ✅ CA logo placeholder (or your uploaded logo)

---

## 📸 Test Bulk Client Upload

1. Go to **"Clients"** in sidebar
2. Click **"Bulk Upload"** (purple button)
3. Create test Excel file:

**clients.xlsx**:
| Phone       | Name          | Email              |
|-------------|---------------|--------------------|
| 9876543210  | Test Client 1 | test1@example.com  |
| +919876543211 | Test Client 2 | test2@example.com |
| 919876543212 | Test Client 3 | test3@example.com |

4. Upload the file
5. See results summary
6. Download credentials CSV

---

## 🔍 Troubleshooting

### **Backend not starting?**
```bash
# Check if port 8443 is in use
lsof -i :8443
# Kill if needed
kill -9 <PID>
```

### **Frontend not starting?**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

### **Database errors?**
```bash
# Reset database
rm ca_desktop.db
alembic upgrade head
# Re-run Step 3 to create user
```

### **Can't login?**
- Check username is exactly: `lokesh` (lowercase)
- Check password matches what you set
- Check backend is running on port 8443

---

## ✅ Success Checklist

Before deploying, verify:

- [ ] Backend running on http://localhost:8443
- [ ] Frontend running on http://localhost:5173
- [ ] Can login at /ca/login
- [ ] Profile updated with your real details
- [ ] 5-10 photos uploaded
- [ ] 4 services added
- [ ] 2-3 testimonials added
- [ ] Website looks good at /ca-lokesh-dagdiya
- [ ] Website is responsive (test on mobile size)
- [ ] All animations working smoothly
- [ ] Contact info is correct
- [ ] Bulk upload works

---

## 🚀 Next: Deploy to Production

Once everything works locally, follow: **DEPLOYMENT_GUIDE.md**

**Deployment will give you**:
- Live URL: `https://your-app.vercel.app/ca-lokesh-dagdiya`
- Free hosting (Vercel + Railway)
- HTTPS automatically
- Available 24/7

---

## 📞 Need Help?

**Common Issues**:
1. **Port already in use**: Change port in backend or frontend
2. **Module not found**: Run `pip install -r requirements.txt` again
3. **Photos not showing**: Check file path in Media Gallery
4. **Website not updating**: Hard refresh browser (Ctrl+Shift+R)

**Your website will be live at**: `https://your-app.vercel.app/ca-lokesh-dagdiya`

---

## 🎉 You're Done!

Your professional CA website is ready with:
- ✅ Dynamic content management
- ✅ Photo gallery (5-10 photos)
- ✅ Smooth transitions and animations
- ✅ Professional design matching bcshettyco.com
- ✅ Fully responsive
- ✅ Client portal integration
- ✅ Bulk client upload feature

**Time to deploy and share with clients!** 🚀
