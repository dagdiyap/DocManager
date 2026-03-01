DocManager CA Desktop - Installation Guide
==========================================

QUICK START
-----------
1. Extract this folder to: C:\Program Files\DocManager
2. (Optional) Edit config/.env.template and save as data/.env
3. Run scripts/start_backend.bat
4. Open browser: http://localhost:5174/ca
5. Login with username: lokesh, password: lokesh

DEFAULT CREDENTIALS
-------------------
CA Login:
  Username: lokesh
  Password: lokesh

Demo Client:
  Phone: 9876543210
  Password: client123

⚠️  CHANGE DEFAULT PASSWORDS AFTER FIRST LOGIN!

FOLDER STRUCTURE
----------------
backend/        - Backend server (DocManager.exe)
frontend/       - Frontend web application
data/           - Database and uploaded documents
  ├── ca_desktop.db  - SQLite database
  ├── uploads/       - Client documents
  └── logs/          - Application logs
config/         - Configuration files
scripts/        - Startup scripts

SYSTEM REQUIREMENTS
-------------------
- Windows 10 or later
- 4 GB RAM minimum (8 GB recommended)
- 20 GB free disk space
- Modern web browser (Chrome, Firefox, Edge)

EMAIL CONFIGURATION
-------------------
To enable email reminders:
1. Sign up free at https://resend.com (3,000 emails/month free)
2. Get API key from dashboard
3. Copy config/.env.template to data/.env
4. Add: RESEND_API_KEY=re_your_key_here
5. Restart application

PORTS USED
----------
- Backend: 8443
- Frontend: 5174

ACCESS URLS
-----------
- CA Dashboard: http://localhost:5174/ca
- Client Portal: http://localhost:5174/portal
- Public Website: http://localhost:5174/ca-lokesh-dagdiya
- API Docs: http://localhost:8443/docs

SUPPORT
-------
For issues, check:
- data/logs/backend.log
- Documentation in docs/guides/

Version: 1.0.0
Released: March 2026
