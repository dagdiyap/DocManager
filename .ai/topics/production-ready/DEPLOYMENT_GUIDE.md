# DocManager Deployment Guide

## Overview

This guide covers deploying DocManager for free hosting (up to 10 CAs) using Vercel for the frontend and Railway/Render for the backend.

---

## Architecture

- **Frontend**: Vercel (Free tier - unlimited bandwidth, 100GB/month)
- **Backend**: Railway/Render (Free tier with limitations)
- **Database**: SQLite (file-based, included with backend)
- **Domain**: Vercel provides free `.vercel.app` subdomain

---

## Prerequisites

1. GitHub account
2. Vercel account (sign up at https://vercel.com)
3. Railway account (sign up at https://railway.app) OR Render account

---

## Part 1: Frontend Deployment (Vercel)

### Step 1: Prepare Repository

```bash
# Ensure code is committed
cd /Users/pdagdiya/DocManager
git add .
git commit -m "Add professional CA website and bulk upload features"
git push origin main
```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com/new
2. Import your GitHub repository
3. Configure build settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `ca_desktop/frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

4. Add Environment Variables:
   ```
   VITE_API_URL=https://your-backend-url.railway.app/api/v1
   ```

5. Click "Deploy"

### Step 3: Configure Custom Domain (Optional)

- In Vercel dashboard → Settings → Domains
- Add custom domain or use provided `.vercel.app` domain
- Example: `docmanager.vercel.app`

---

## Part 2: Backend Deployment (Railway - Recommended)

### Option A: Railway (Easier, Better Free Tier)

1. Go to https://railway.app/new
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Configure:
   - **Root Directory**: `ca_desktop/backend`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

5. Add Environment Variables:
   ```
   DATABASE_URL=sqlite:///./ca_desktop.db
   SECRET_KEY=your-secret-key-here
   BASE_URL=https://docmanager.vercel.app
   RESEND_API_KEY=your-resend-key (optional)
   ```

6. Railway will provide a URL like: `https://your-app.railway.app`

### Option B: Render (Alternative)

1. Go to https://render.com/new/web-service
2. Connect GitHub repository
3. Configure:
   - **Root Directory**: `ca_desktop/backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`

4. Add Environment Variables (same as Railway)

---

## Part 3: Database Setup

### Initialize Database

```bash
# SSH into Railway/Render instance or use web shell
cd ca_desktop/backend
alembic upgrade head
```

### Create Test CA User (Lokesh Dagdiya)

```python
# Run this in Python shell on backend
from src.database import SessionLocal
from src.models import User
from src.dependencies import get_password_hash

db = SessionLocal()

ca_user = User(
    username="lokesh",
    email="lokesh@example.com",
    password_hash=get_password_hash("test123"),
    display_name="CA Lokesh Dagdiya",
    slug="lokesh-dagdiya",
)
db.add(ca_user)
db.commit()
print(f"Created CA user: {ca_user.username}")
```

---

## Part 4: Update Frontend with Backend URL

1. In Vercel dashboard → Settings → Environment Variables
2. Update `VITE_API_URL` to your Railway/Render URL
3. Redeploy frontend

---

## Part 5: Test the Deployment

### Test CA Website

1. Visit: `https://docmanager.vercel.app/ca-lokesh-dagdiya`
2. Should see professional CA website
3. Click "Client Login" → Should redirect to login page

### Test Bulk Upload

1. Login to CA dashboard: `https://docmanager.vercel.app/ca/login`
2. Username: `lokesh`, Password: `test123`
3. Go to Clients → Click "Bulk Upload"
4. Upload test Excel file

---

## Sample Test Data

### Excel File Format (clients.xlsx)

| Phone       | Name          | Email              |
|-------------|---------------|--------------------|
| 9876543210  | Amit Sharma   | amit@example.com   |
| +919876543211 | Priya Patel | priya@example.com  |
| 919876543212 | Rahul Kumar  | rahul@example.com  |

### Text File Format (clients.txt)

```
9876543210,Amit Sharma,amit@example.com
+919876543211,Priya Patel,priya@example.com
919876543212,Rahul Kumar,rahul@example.com
9876543213
+919876543214
```

---

## Free Tier Limitations

### Vercel (Frontend)
- ✅ Unlimited bandwidth
- ✅ 100GB bandwidth/month
- ✅ Automatic HTTPS
- ✅ Global CDN
- ✅ Perfect for 10 CAs

### Railway (Backend)
- ✅ 500 hours/month (enough for 24/7 with 1 service)
- ✅ 1GB RAM
- ✅ 1GB disk
- ⚠️ Sleeps after 30min inactivity (wakes on request)

### Render (Backend Alternative)
- ✅ 750 hours/month
- ✅ 512MB RAM
- ⚠️ Spins down after 15min inactivity
- ⚠️ Slower cold starts

---

## Scaling Beyond 10 CAs

When you exceed 10 CAs:

1. **Upgrade Railway**: $5/month for 8GB RAM, no sleep
2. **Or use Render**: $7/month for always-on
3. **Or use DigitalOcean**: $4/month droplet
4. **Database**: Migrate to PostgreSQL (free on Railway/Render)

---

## Monitoring & Maintenance

### Health Checks

- Backend: `https://your-backend.railway.app/health`
- Frontend: `https://docmanager.vercel.app`

### Logs

- **Vercel**: Dashboard → Deployments → View Logs
- **Railway**: Dashboard → Deployments → View Logs

### Backups

```bash
# Backup SQLite database
scp railway:/app/ca_desktop.db ./backups/ca_desktop_$(date +%Y%m%d).db
```

---

## Troubleshooting

### Issue: Backend not responding
- Check Railway/Render logs
- Verify environment variables
- Check if service is sleeping (free tier)

### Issue: Frontend can't connect to backend
- Verify `VITE_API_URL` in Vercel env vars
- Check CORS settings in backend
- Ensure backend is deployed and running

### Issue: Database errors
- Run migrations: `alembic upgrade head`
- Check database file permissions
- Verify SQLite is installed

---

## Security Checklist

- ✅ Change default SECRET_KEY
- ✅ Use HTTPS (automatic with Vercel/Railway)
- ✅ Set up RESEND_API_KEY for emails
- ✅ Enable rate limiting (already configured)
- ✅ Regular database backups
- ✅ Monitor logs for suspicious activity

---

## Cost Estimate

| Service | Free Tier | Paid (if needed) |
|---------|-----------|------------------|
| Vercel  | ✅ Free   | $20/month (Pro)  |
| Railway | ✅ Free   | $5/month (Hobby) |
| Resend  | ✅ 100 emails/day | $10/month |
| **Total** | **$0/month** | **$15-35/month** |

---

## Next Steps

1. ✅ Deploy frontend to Vercel
2. ✅ Deploy backend to Railway
3. ✅ Create Lokesh Dagdiya CA user
4. ✅ Test website at `/ca-lokesh-dagdiya`
5. ✅ Test bulk upload feature
6. ✅ Share URL with Lokesh for feedback

---

## Support

For issues or questions:
- Check logs in Vercel/Railway dashboard
- Review this guide
- Test locally first before deploying
