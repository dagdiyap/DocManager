# DocManager CA Desktop - Deployment Guide

**Production Deployment Instructions**  
**Version**: 1.0  
**Last Updated**: March 2026

---

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Pre-Deployment Checklist](#pre-deployment-checklist)
3. [Local Installation (CA Computer)](#local-installation-ca-computer)
4. [Configuration](#configuration)
5. [Database Setup](#database-setup)
6. [Running in Production](#running-in-production)
7. [Backup & Recovery](#backup--recovery)
8. [Updates & Maintenance](#updates--maintenance)
9. [Security Best Practices](#security-best-practices)
10. [Troubleshooting](#troubleshooting)

---

## Deployment Overview

DocManager CA Desktop is designed to run **locally on the CA's computer** as a desktop application. It does not require cloud hosting or internet connectivity for core functionality.

### Deployment Model

```
┌────────────────────────────────────┐
│      CA's Computer (Windows/Mac)   │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  Backend Server              │ │
│  │  (Python + FastAPI)          │ │
│  │  Port: 8443                  │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  Frontend Server             │ │
│  │  (React + Vite)              │ │
│  │  Port: 5174                  │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  SQLite Database             │ │
│  │  (ca_desktop.db)             │ │
│  └──────────────────────────────┘ │
│                                    │
│  ┌──────────────────────────────┐ │
│  │  Document Storage            │ │
│  │  (data/uploads/)             │ │
│  └──────────────────────────────┘ │
└────────────────────────────────────┘

Access from same network:
- CA: http://localhost:5174/ca
- Clients: http://<CA-IP>:5174/portal
```

---

## Pre-Deployment Checklist

### System Requirements

**Minimum**:
- CPU: Dual-core processor
- RAM: 4 GB
- Storage: 20 GB available (more for documents)
- OS: Windows 10+, macOS 10.15+, or Linux

**Recommended**:
- CPU: Quad-core processor
- RAM: 8 GB+
- Storage: 100 GB+ SSD
- OS: Latest stable version

### Software Requirements

- [ ] Python 3.14.2 or compatible version
- [ ] Node.js 18+ and npm
- [ ] Git (for updates)
- [ ] Web browser (Chrome, Firefox, Safari, Edge)

### Pre-Installation Steps

1. [ ] Backup existing data (if upgrading)
2. [ ] Verify system requirements
3. [ ] Install required software
4. [ ] Obtain Resend API key (for emails)
5. [ ] Prepare CA credentials
6. [ ] Test network connectivity
7. [ ] Disable conflicting software

---

## Local Installation (CA Computer)

### Step 1: Download Application

```bash
# Option A: Git clone
git clone <repository-url>
cd DocManager

# Option B: Download ZIP
# Extract to desired location (e.g., C:\DocManager or ~/DocManager)
cd DocManager
```

### Step 2: Install Python Dependencies

#### Windows:
```powershell
cd ca_desktop\backend
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

#### macOS/Linux:
```bash
cd ca_desktop/backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

**Expected Time**: 5-10 minutes

### Step 3: Install Frontend Dependencies

```bash
cd ca_desktop/frontend
npm install
```

**Expected Time**: 3-5 minutes

### Step 4: Setup Database

```bash
# Return to project root
cd ../..

# Activate Python environment
source ca_desktop/backend/venv/bin/activate  # macOS/Linux
# OR
ca_desktop\backend\venv\Scripts\activate  # Windows

# Initialize database
python scripts/setup_database.py

# Optional: Add demo data for testing
python scripts/setup_demo_data.py
```

### Step 5: Create CA Admin Account

The setup script creates a default CA account:
- **Username**: lokesh
- **Password**: lokesh

**⚠️ IMPORTANT**: Change this password immediately after first login!

### Step 6: Configure Environment

Create `.env` file in project root:

```bash
# Required for email reminders
RESEND_API_KEY=re_your_api_key_here

# Optional configurations
DATABASE_URL=sqlite:///./ca_desktop.db
SECRET_KEY=your-secret-key-here
FRONTEND_URL=http://localhost:5174
```

**Getting Resend API Key**:
1. Visit https://resend.com/
2. Sign up for free account
3. Get API key from dashboard
4. Add to `.env` file

---

## Configuration

### Network Configuration

#### For CA Only (Default)
No additional configuration needed. Access at `http://localhost:5174`

#### For Client Portal Access (Same Network)

1. **Find CA Computer IP**:
   ```bash
   # Windows
   ipconfig
   
   # macOS/Linux
   ifconfig
   ```
   Example IP: `192.168.1.100`

2. **Update Frontend URL** in `.env`:
   ```bash
   FRONTEND_URL=http://192.168.1.100:5174
   ```

3. **Configure Firewall**:
   - Allow inbound on port 5174 (frontend)
   - Allow inbound on port 8443 (backend)
   
   **Windows Firewall**:
   ```powershell
   netsh advfirewall firewall add rule name="DocManager Frontend" dir=in action=allow protocol=TCP localport=5174
   netsh advfirewall firewall add rule name="DocManager Backend" dir=in action=allow protocol=TCP localport=8443
   ```

4. **Share with Clients**:
   - CA Dashboard: `http://192.168.1.100:5174/ca`
   - Client Portal: `http://192.168.1.100:5174/portal`
   - Public Website: `http://192.168.1.100:5174/ca-lokesh-dagdiya`

### Email Configuration

For reminder emails to work:

1. **Get Resend API Key** (required)
2. **Add to `.env`**:
   ```bash
   RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
3. **Verify sender domain** (for production emails)

### Storage Configuration

Default document storage: `data/uploads/`

**Change Location**:
1. Edit `ca_desktop/backend/src/config.py`
2. Update `UPLOAD_DIR` path
3. Ensure write permissions

---

## Database Setup

### Initial Setup

Database is automatically created during installation at: `ca_desktop.db`

### Database Location

**Default**: Project root directory

**Custom Location**:
Edit `.env`:
```bash
DATABASE_URL=sqlite:///path/to/custom/location/ca_desktop.db
```

### Database Structure

Tables created automatically:
- `users` - CA users
- `clients` - Client accounts
- `documents` - Uploaded documents
- `reminders` - Reminder records
- `ca_profiles` - CA profile information
- `ca_services` - Services offered
- `ca_testimonials` - Client testimonials
- `compliance_rules` - Compliance requirements
- `media_items` - Website media

### Database Maintenance

```bash
# Check database size
ls -lh ca_desktop.db

# Vacuum (optimize)
sqlite3 ca_desktop.db "VACUUM;"

# Check integrity
sqlite3 ca_desktop.db "PRAGMA integrity_check;"
```

---

## Running in Production

### Startup Script

Use the provided startup script:

```bash
./start.sh
```

This script:
1. Activates Python virtual environment
2. Upgrades pip and dependencies
3. Starts backend server
4. Starts frontend server
5. Provides access URLs

### Manual Start (Alternative)

**Terminal 1 - Backend**:
```bash
cd ca_desktop/backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8443
```

**Terminal 2 - Frontend**:
```bash
cd ca_desktop/frontend
npm run dev -- --host 0.0.0.0
```

### Auto-Start on Boot

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When the computer starts"
4. Action: "Start a program"
5. Program: `C:\DocManager\start.sh`
6. Advanced: Run whether user is logged in or not

#### macOS (LaunchAgent)

Create `~/Library/LaunchAgents/com.docmanager.app.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.docmanager.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/DocManager/start.sh</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

Load:
```bash
launchctl load ~/Library/LaunchAgents/com.docmanager.app.plist
```

#### Linux (systemd)

Create `/etc/systemd/system/docmanager.service`:
```ini
[Unit]
Description=DocManager CA Desktop
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/path/to/DocManager
ExecStart=/path/to/DocManager/start.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl enable docmanager
sudo systemctl start docmanager
```

### Production vs Development Mode

**Development** (default):
- Hot reload enabled
- Debug mode on
- Detailed error messages

**Production**:
Edit `start.sh`:
```bash
# Backend
uvicorn src.main:app --host 0.0.0.0 --port 8443 --workers 4

# Frontend
npm run build
npm run preview -- --host 0.0.0.0
```

---

## Backup & Recovery

### What to Backup

1. **Database**: `ca_desktop.db`
2. **Documents**: `data/uploads/`
3. **Configuration**: `.env`
4. **Logs** (optional): `logs/`

### Backup Strategy

#### Manual Backup

```bash
# Create backup directory
mkdir -p backups/$(date +%Y%m%d)

# Backup database
cp ca_desktop.db backups/$(date +%Y%m%d)/

# Backup documents
cp -r data/uploads backups/$(date +%Y%m%d)/

# Backup config
cp .env backups/$(date +%Y%m%d)/
```

#### Automated Backup Script

Create `backup.sh`:
```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/$DATE"

mkdir -p "$BACKUP_PATH"

# Backup database
cp ca_desktop.db "$BACKUP_PATH/"

# Backup documents
cp -r data/uploads "$BACKUP_PATH/"

# Backup config
cp .env "$BACKUP_PATH/"

# Compress
tar -czf "$BACKUP_PATH.tar.gz" "$BACKUP_PATH"
rm -rf "$BACKUP_PATH"

# Keep only last 30 backups
ls -t "$BACKUP_DIR"/*.tar.gz | tail -n +31 | xargs rm -f

echo "Backup completed: $BACKUP_PATH.tar.gz"
```

Schedule daily:
```bash
# cron (Linux/macOS)
0 2 * * * /path/to/DocManager/backup.sh

# Task Scheduler (Windows)
# Create daily task at 2 AM
```

### Recovery

```bash
# Stop application
pkill -f "uvicorn"
pkill -f "vite"

# Restore database
cp backups/20260301/ca_desktop.db ./

# Restore documents
rm -rf data/uploads
cp -r backups/20260301/uploads data/

# Restore config
cp backups/20260301/.env ./

# Restart application
./start.sh
```

---

## Updates & Maintenance

### Updating Application

```bash
# 1. Stop application
pkill -f "uvicorn"
pkill -f "vite"

# 2. Backup current version
./backup.sh

# 3. Pull updates
git pull origin main

# 4. Update backend dependencies
cd ca_desktop/backend
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 5. Update frontend dependencies
cd ../frontend
npm install

# 6. Run database migrations (if any)
# python scripts/migrate_database.py

# 7. Restart application
cd ../..
./start.sh
```

### Version Checking

Check current version:
```bash
# Backend
curl http://localhost:8443/api/v1/health

# Frontend
# Check package.json version
```

### Maintenance Schedule

| Task | Frequency | Command |
|------|-----------|---------|
| Backup | Daily | `./backup.sh` |
| Database vacuum | Weekly | `sqlite3 ca_desktop.db "VACUUM;"` |
| Log rotation | Weekly | `rm logs/*.log` |
| Update check | Monthly | `git fetch` |
| Security updates | As needed | `pip install --upgrade` |

---

## Security Best Practices

### 1. Change Default Credentials

```bash
# Login as default CA
# Go to Profile → Change Password
# Set strong password
```

### 2. Secure Database

```bash
# Set file permissions (Linux/macOS)
chmod 600 ca_desktop.db

# Windows: Right-click → Properties → Security
# Remove all users except current user
```

### 3. Protect .env File

```bash
# Never commit to git
echo ".env" >> .gitignore

# Set permissions
chmod 600 .env
```

### 4. Enable HTTPS (Optional)

For production with client access:

1. **Obtain SSL certificate**
2. **Configure nginx/Apache** as reverse proxy
3. **Update URLs** to use https://

### 5. Firewall Rules

Only open required ports:
- Port 5174 (frontend) - for client access
- Port 8443 (backend) - for API access

Block external access if not needed.

### 6. Regular Backups

- Daily automatic backups
- Test recovery process monthly
- Store backups securely

### 7. Update Management

- Check for updates monthly
- Apply security patches immediately
- Test updates in staging first

### 8. Access Control

- Use strong passwords
- Limit client portal access to trusted network
- Monitor access logs

---

## Troubleshooting

### Application Won't Start

**Check ports**:
```bash
# Check if ports are in use
lsof -i :5174
lsof -i :8443

# Kill processes if needed
kill -9 <PID>
```

**Check logs**:
```bash
tail -f logs/backend.log
tail -f logs/frontend.log
```

### Database Locked Error

```bash
# Stop all processes
pkill -f "uvicorn"

# Remove lock files
rm ca_desktop.db-wal
rm ca_desktop.db-shm

# Restart
./start.sh
```

### Cannot Access from Client Devices

1. **Verify CA IP address**:
   ```bash
   ifconfig  # macOS/Linux
   ipconfig  # Windows
   ```

2. **Test connectivity**:
   ```bash
   # From client device
   ping <CA-IP>
   curl http://<CA-IP>:5174
   ```

3. **Check firewall**:
   - Ensure ports 5174 and 8443 are open
   - Temporarily disable firewall to test

4. **Verify network**:
   - CA and clients on same network
   - No VPN interference

### Email Reminders Not Sending

1. **Check Resend API key**:
   ```bash
   cat .env | grep RESEND_API_KEY
   ```

2. **Test API key**:
   ```bash
   curl -X POST https://api.resend.com/emails \
     -H "Authorization: Bearer re_your_key" \
     -H "Content-Type: application/json"
   ```

3. **Check logs**:
   ```bash
   grep "email" logs/backend.log
   ```

### Database Corruption

```bash
# Check integrity
sqlite3 ca_desktop.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cp backups/latest/ca_desktop.db ./

# If no backup, try to recover
sqlite3 ca_desktop.db ".recover" | sqlite3 recovered.db
mv recovered.db ca_desktop.db
```

### Performance Issues

1. **Check disk space**:
   ```bash
   df -h
   ```

2. **Optimize database**:
   ```bash
   sqlite3 ca_desktop.db "VACUUM;"
   sqlite3 ca_desktop.db "ANALYZE;"
   ```

3. **Clear old logs**:
   ```bash
   rm logs/*.log
   ```

4. **Archive old documents**:
   - Move old year documents to archive
   - Keep active years only

---

## Production Checklist

Before going live:

- [ ] System requirements verified
- [ ] All dependencies installed
- [ ] Database created and tested
- [ ] Default password changed
- [ ] Email configured (Resend API key)
- [ ] Backup system in place
- [ ] Firewall configured
- [ ] Network access tested
- [ ] Auto-start configured
- [ ] Documentation reviewed
- [ ] Test all features
- [ ] Train CA user
- [ ] Support plan in place

---

## Support & Maintenance

### Log Files

- **Backend**: `logs/backend.log`
- **Frontend**: Browser console
- **Database**: SQLite error messages

### Health Monitoring

Check system health:
```bash
curl http://localhost:8443/api/v1/health
```

Response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-01T12:00:00"
}
```

### Performance Monitoring

Monitor:
- Response times
- Database size
- Disk space
- Memory usage

---

## Migration from Other Systems

### Data Import

1. **Export data** from existing system
2. **Format as CSV/JSON**
3. **Use import script**:
   ```bash
   python scripts/import_data.py --clients clients.csv --documents docs.csv
   ```

### Manual Migration

1. Create clients via API/UI
2. Upload documents for each client
3. Set up reminders as needed

---

**DocManager CA Desktop** - Deployment Guide

*For technical support during deployment, refer to troubleshooting section or contact support team.*
