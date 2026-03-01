# Production Deployment Checklist

**DocManager CA Desktop - v1.0.0**  
**Pre-Deployment Verification**

---

## 📋 Pre-Installation Checklist

### System Verification
- [ ] Operating system meets minimum requirements (Windows 10+, macOS 10.15+, Linux)
- [ ] CPU: Dual-core or better
- [ ] RAM: 4 GB minimum (8 GB recommended)
- [ ] Storage: 20 GB minimum available (100 GB+ recommended)
- [ ] Network connectivity available for email features

### Software Prerequisites
- [ ] Python 3.14.2 installed and accessible
- [ ] Node.js 18+ installed
- [ ] npm available
- [ ] Git installed (for updates)
- [ ] Modern web browser installed

### Pre-Installation Preparation
- [ ] Backup any existing data
- [ ] Download/clone application files
- [ ] Obtain Resend API key for email functionality
- [ ] Prepare CA credentials and firm information
- [ ] Identify target installation directory
- [ ] Check firewall requirements

---

## 🛠️ Installation Checklist

### Backend Setup
- [ ] Navigate to project directory
- [ ] Create Python virtual environment (`python -m venv ca_desktop/backend/venv`)
- [ ] Activate virtual environment
- [ ] Upgrade pip, setuptools, wheel
- [ ] Install backend dependencies (`pip install -r requirements.txt`)
- [ ] Verify all dependencies installed without errors

### Frontend Setup
- [ ] Navigate to frontend directory (`cd ca_desktop/frontend`)
- [ ] Install npm dependencies (`npm install`)
- [ ] Verify all packages installed successfully
- [ ] No critical vulnerabilities in dependencies

### Database Setup
- [ ] Run database initialization script (`python scripts/setup_database.py`)
- [ ] Verify `ca_desktop.db` file created
- [ ] Check database has all required tables
- [ ] Optionally load demo data (`python scripts/setup_demo_data.py`)

### Configuration
- [ ] Create `.env` file in project root
- [ ] Add `RESEND_API_KEY` for email functionality
- [ ] Configure optional settings (DATABASE_URL, FRONTEND_URL)
- [ ] Verify `.env` file permissions (should not be world-readable)
- [ ] Add `.env` to `.gitignore`

---

## 🧪 Testing Checklist

### API Tests
- [ ] Run API test suite (`python tests/api/test_api_complete.py`)
- [ ] All authentication tests pass
- [ ] All client management tests pass
- [ ] All document tests pass
- [ ] All reminder tests pass
- [ ] All CA profile tests pass
- [ ] Public API tests pass
- [ ] Compliance tests pass
- [ ] Health check passes
- [ ] **Target: 100% pass rate**

### E2E Workflow Tests
- [ ] Run workflow tests (`python tests/workflows/test_e2e_workflows.py`)
- [ ] Client onboarding workflow passes
- [ ] Document management workflow passes
- [ ] Reminder system workflow passes
- [ ] Client portal workflow passes
- [ ] Public website workflow passes
- [ ] Compliance tracking workflow passes
- [ ] Tax season workflow passes
- [ ] **Target: 100% pass rate**

### Quick System Test
- [ ] Run quick test (`python scripts/test_everything.py`)
- [ ] All services running
- [ ] Authentication working
- [ ] Client operations working
- [ ] Document operations working
- [ ] Reminders working
- [ ] Frontend pages accessible

### Manual UI Testing
- [ ] Start application (`./start.sh`)
- [ ] Backend accessible at http://localhost:8443/docs
- [ ] Frontend accessible at http://localhost:5174
- [ ] CA login page loads correctly
- [ ] Login with default credentials works
- [ ] Dashboard displays correctly
- [ ] Navigation between sections works
- [ ] All menu items accessible

### Feature Testing
- [ ] **Client Management**
  - [ ] Can create new client
  - [ ] Client directory created automatically
  - [ ] Client appears in list
  - [ ] Can view client details
  - [ ] Can update client information
  - [ ] Client type displays correctly

- [ ] **Document Management**
  - [ ] Can upload single document
  - [ ] Can upload multiple documents
  - [ ] Can upload folder
  - [ ] Documents organized by client and year
  - [ ] Can browse documents by client
  - [ ] Back button works
  - [ ] Can preview documents
  - [ ] Full filename visible on hover
  - [ ] Can download documents

- [ ] **Reminder System**
  - [ ] Document types dropdown populated
  - [ ] Can select multiple clients
  - [ ] Can add multiple documents
  - [ ] Document type selection works
  - [ ] Year input works
  - [ ] Email/WhatsApp checkboxes work
  - [ ] Can add general instructions
  - [ ] Submit creates correct number of reminders
  - [ ] Success message shows counts
  - [ ] Reminders appear in list
  - [ ] Can filter reminders by client

- [ ] **CA Profile & Public Website**
  - [ ] Can update CA profile
  - [ ] Firm name saves correctly
  - [ ] Can add services
  - [ ] Can add testimonials
  - [ ] Can upload media
  - [ ] Public website accessible
  - [ ] "Welcome to Dagdiya Associates" displays
  - [ ] CA color scheme visible
  - [ ] Service cards display with icons
  - [ ] Contact information shows
  - [ ] Responsive on mobile

- [ ] **Client Portal**
  - [ ] Portal login page accessible
  - [ ] Can login with client credentials
  - [ ] Client sees their documents
  - [ ] Can download documents
  - [ ] Can view reminders
  - [ ] Mobile responsive

---

## 🔒 Security Checklist

### Credentials
- [ ] **CRITICAL**: Change default CA password from `lokesh`
- [ ] Set strong password (12+ characters, mixed case, numbers, symbols)
- [ ] Change demo client password
- [ ] Document new credentials securely (not in code)

### Database Security
- [ ] Set appropriate file permissions on `ca_desktop.db` (owner read/write only)
- [ ] Database not in publicly accessible location
- [ ] Regular backups configured

### Configuration Security
- [ ] `.env` file has restricted permissions (600)
- [ ] `.env` in `.gitignore`
- [ ] No API keys in source code
- [ ] No passwords in source code

### Network Security
- [ ] Firewall configured appropriately
- [ ] Only necessary ports open (5174, 8443)
- [ ] If client access needed, network properly configured
- [ ] If external access needed, consider VPN or SSH tunnel

### Application Security
- [ ] JWT tokens properly configured
- [ ] Session timeout appropriate
- [ ] No debug mode in production
- [ ] Error messages don't leak sensitive information

---

## 💾 Backup Checklist

### Backup Strategy
- [ ] Backup location identified
- [ ] Automated backup script created
- [ ] Backup schedule configured (recommended: daily)
- [ ] Test backup script execution

### What to Backup
- [ ] Database file (`ca_desktop.db`)
- [ ] Document storage (`data/uploads/`)
- [ ] Configuration file (`.env`)
- [ ] Application logs (`logs/`)

### Backup Verification
- [ ] Perform manual backup test
- [ ] Verify backup files created
- [ ] Test restoration process
- [ ] Document restoration procedure
- [ ] Set backup retention policy (recommended: 30 days)

---

## 🚀 Startup Configuration

### Auto-Start Setup (Optional)
- [ ] Choose auto-start method (Task Scheduler/LaunchAgent/systemd)
- [ ] Configure auto-start
- [ ] Test auto-start on reboot
- [ ] Verify services start correctly
- [ ] Document auto-start configuration

### Service Verification
- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Both services accessible after auto-start
- [ ] Logs show normal startup

---

## 📊 Performance & Monitoring

### Performance Checks
- [ ] Application response time acceptable (<2 seconds)
- [ ] Document upload completes successfully
- [ ] Page navigation smooth
- [ ] No memory leaks observed
- [ ] Database queries performant

### Monitoring Setup
- [ ] Log rotation configured
- [ ] Disk space monitoring in place
- [ ] Database size monitoring
- [ ] Error logging functional
- [ ] Access logs enabled

---

## 📚 Documentation Checklist

### User Documentation
- [ ] User Guide accessible to CA (`docs/guides/USER_GUIDE.md`)
- [ ] CA trained on basic operations
- [ ] Client portal instructions prepared
- [ ] Quick reference guide available

### Technical Documentation
- [ ] Developer Guide available (`docs/guides/DEVELOPER_GUIDE.md`)
- [ ] Deployment Guide available (`docs/guides/DEPLOYMENT_GUIDE.md`)
- [ ] README.md complete and accurate
- [ ] API documentation accessible (http://localhost:8443/docs)

### Operational Documentation
- [ ] Backup procedure documented
- [ ] Recovery procedure documented
- [ ] Troubleshooting guide accessible
- [ ] Support contact information documented
- [ ] Update procedure documented

---

## 🌐 Client Access Configuration (If Required)

### Network Setup
- [ ] CA computer IP address identified
- [ ] Firewall configured for ports 5174 and 8443
- [ ] Network allows client connections
- [ ] Client access URLs documented

### Client Portal Setup
- [ ] Client accounts created
- [ ] Portal passwords set
- [ ] Portal URL shared with clients
- [ ] Login instructions provided to clients
- [ ] Test client login from another device

---

## ✅ Final Verification

### System Health
- [ ] Run complete test suite one final time
- [ ] All tests passing (100%)
- [ ] No errors in logs
- [ ] All features functional
- [ ] Performance acceptable

### Pre-Go-Live
- [ ] All checklist items completed
- [ ] CA user trained
- [ ] Support plan in place
- [ ] Rollback plan documented
- [ ] Go-live date confirmed

### Post-Deployment
- [ ] Monitor system for 24 hours
- [ ] Check logs daily for first week
- [ ] Verify backups running
- [ ] Client feedback collected
- [ ] Document any issues and resolutions

---

## 📞 Support Information

### Emergency Contacts
- **Technical Support**: [Insert contact]
- **System Administrator**: [Insert contact]

### Key Resources
- User Guide: `docs/guides/USER_GUIDE.md`
- Troubleshooting: `docs/guides/DEPLOYMENT_GUIDE.md#troubleshooting`
- Logs Location: `logs/`
- Database Location: `ca_desktop.db`

### Common Issues Quick Reference
| Issue | Quick Fix |
|-------|-----------|
| Won't start | Check ports with `lsof -i :5174` and `lsof -i :8443` |
| Database locked | Stop all processes, remove `.db-wal` and `.db-shm` files |
| Email not sending | Verify `RESEND_API_KEY` in `.env` |
| Client can't access | Check firewall, verify IP, ensure same network |

---

## 🎯 Success Criteria

### Must Have (Critical)
- ✅ All automated tests pass at 100%
- ✅ CA can login and access dashboard
- ✅ Can create clients
- ✅ Can upload documents
- ✅ Can create reminders
- ✅ Default password changed
- ✅ Backups configured

### Should Have (Important)
- ✅ Auto-start configured
- ✅ Client portal accessible
- ✅ Public website functional
- ✅ Email reminders working
- ✅ CA profile complete

### Nice to Have (Optional)
- ⭕ Custom CA branding
- ⭕ Additional services configured
- ⭕ Testimonials added
- ⭕ Multiple CA users

---

## 📝 Sign-Off

### Deployment Team
- [ ] **Technical Lead**: _______________ Date: ___________
- [ ] **System Administrator**: _______________ Date: ___________
- [ ] **CA User (Lokesh)**: _______________ Date: ___________

### Deployment Status
- [ ] **Ready for Production**: All critical items completed
- [ ] **Go-Live Approved**: Authorized to deploy
- [ ] **Post-Deployment Review Scheduled**: Date: ___________

---

**DocManager CA Desktop v1.0.0** - Production Deployment Checklist

*Complete all items before deploying to production environment*

**Last Updated**: March 2026
