# Deploy DocManager to GitHub & Vercel

## ✅ Step 1: Create GitHub Repository

1. Go to: https://github.com/new
2. Repository name: `DocManager`
3. Description: `Document Management System for Chartered Accountants`
4. **Keep it Private** (recommended for now)
5. **DO NOT** initialize with README (we already have one)
6. Click "Create repository"

## ✅ Step 2: Push Code to GitHub

After creating the repository, run these commands:

```bash
cd /Users/pdagdiya/DocManager

# Add the remote (use YOUR actual GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/DocManager.git

# Push all code
git push -u origin main
```

**✅ SAFE TO PUSH:** All sensitive files are already excluded:
- ✅ `.env` files are in `.gitignore`
- ✅ Database files excluded
- ✅ Private keys excluded
- ✅ Logs excluded
- ✅ `.env.example` included (template only)

## ✅ Step 3: Deploy Frontend to Vercel

### Option A: Deploy via Vercel CLI (Fastest)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd /Users/pdagdiya/DocManager
vercel --prod
```

**Vercel will ask:**
1. "Set up and deploy?" → **Yes**
2. "Which scope?" → Select your account
3. "Link to existing project?" → **No**
4. "Project name?" → `docmanager-ca` (or any name)
5. "Directory?" → `./` (root)
6. "Override settings?" → **No**

**Result:** Live at `https://docmanager-ca.vercel.app`

### Option B: Deploy via Vercel Dashboard (Easier)

1. Go to: https://vercel.com/new
2. Click "Import Git Repository"
3. Select your GitHub repo: `DocManager`
4. **Root Directory:** Leave as `./`
5. **Build Command:** `cd ca_desktop/frontend && npm install && npm run build`
6. **Output Directory:** `ca_desktop/frontend/dist`
7. **Install Command:** `cd ca_desktop/frontend && npm install`
8. Click "Deploy"

## ✅ Step 4: Configure Vercel for CA Website

### Update vercel.json (Already Done)

The `vercel.json` is already configured for multi-tenant routing:
- `/ca-lokesh-dagdiya` → Lokesh's website
- `/ca-lokesh-dagdiya/login` → Client portal
- All routes handled by React Router

### Set Environment Variables in Vercel

1. Go to: https://vercel.com/YOUR_USERNAME/docmanager-ca/settings/environment-variables
2. Add these variables:

```
VITE_API_URL = https://your-backend-url.com/api/v1
```

**For now (testing):** Use `http://localhost:8443/api/v1`
**For production:** Deploy backend to Railway (see below)

## ✅ Step 5: Test the Deployed Website

Once deployed, visit:
- **Lokesh's Website:** `https://docmanager-ca.vercel.app/ca-lokesh-dagdiya`
- **Client Login:** `https://docmanager-ca.vercel.app/ca-lokesh-dagdiya/login`

**Expected:**
- ✅ Professional website with Lokesh's photo
- ✅ HD financial images
- ✅ Services, testimonials, contact info
- ✅ "Client Login" button works
- ⚠️ Login won't work yet (backend not deployed)

## ✅ Step 6: Deploy Backend to Railway (Optional - for 24/7 access)

### Why Railway?
- ✅ Free tier: 500 hours/month (enough for 1 CA)
- ✅ Easy deployment from GitHub
- ✅ PostgreSQL database included
- ✅ Auto-deploy on git push

### Steps:

1. Go to: https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `DocManager` repository
4. **Root Directory:** `ca_desktop/backend`
5. **Start Command:** `uvicorn ca_desktop.backend.src.main:app --host 0.0.0.0 --port $PORT`

6. **Add Environment Variables:**
```
SECRET_KEY=<generate-a-random-32-char-string>
DATABASE_URL=<railway-will-provide-this>
CORS_ORIGINS=https://docmanager-ca.vercel.app,http://localhost:5174
```

7. Click "Deploy"

8. **Get Backend URL:** `https://docmanager-ca-production.up.railway.app`

9. **Update Vercel Environment:**
   - Go back to Vercel settings
   - Update `VITE_API_URL` to Railway backend URL
   - Redeploy Vercel

## ✅ Step 7: Custom Domain (Optional)

### For Lokesh's Website:

1. **Buy Domain:** `lokeshdagdiya.com` (~$10/year)
   - Namecheap, GoDaddy, or Google Domains

2. **Add to Vercel:**
   - Vercel Dashboard → Settings → Domains
   - Add `lokeshdagdiya.com`
   - Follow DNS instructions

3. **Result:** `https://lokeshdagdiya.com/ca-lokesh-dagdiya`

## 🎯 Quick Deploy Summary

### Minimum (Static Website Only):
```bash
# 1. Create GitHub repo at github.com/new
# 2. Push code
git remote add origin https://github.com/YOUR_USERNAME/DocManager.git
git push -u origin main

# 3. Deploy to Vercel
vercel --prod
```

**Result:** Public website live in 5 minutes!

### Full Stack (Website + Backend):
1. Deploy frontend to Vercel (above)
2. Deploy backend to Railway
3. Update Vercel env vars with Railway URL
4. Redeploy Vercel

**Result:** Fully functional system with 24/7 uptime!

## 🔒 Security Checklist

Before deploying:
- ✅ `.env` files excluded from git
- ✅ SECRET_KEY not in code (auto-generated)
- ✅ Database files excluded
- ✅ Private keys excluded
- ✅ `.env.example` provided for documentation

**All secure!** Safe to push to GitHub.

## 📞 For Your Demo Today

### Quick Test (Local):
```bash
cd /Users/pdagdiya/DocManager
./start.sh
```
Open: http://localhost:5174/ca-lokesh-dagdiya

### Deploy Live (5 minutes):
1. Create GitHub repo
2. Push code: `git push -u origin main`
3. Deploy Vercel: `vercel --prod`
4. Share URL: `https://docmanager-ca.vercel.app/ca-lokesh-dagdiya`

**That's it!** Lokesh can access his website 24/7.

## 🆘 Troubleshooting

### "Repository not found"
- Create the GitHub repository first at github.com/new
- Use correct username in remote URL

### "Build failed on Vercel"
- Check build command includes `cd ca_desktop/frontend`
- Verify `package.json` exists in frontend folder

### "Website shows 404"
- Check `vercel.json` routing configuration
- Ensure React Router handles all routes

### "API calls fail"
- Backend not deployed yet (expected)
- Deploy backend to Railway for full functionality
- Or keep backend local for demo

## 📝 Next Steps After Deployment

1. **Test the live website**
2. **Share URL with Lokesh**
3. **Decide on backend hosting** (Railway for 24/7, or local for demo)
4. **Add custom domain** (optional)
5. **Onboard real clients**

---

**Ready to deploy?** Start with Step 1: Create GitHub repository!
