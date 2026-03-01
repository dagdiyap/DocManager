# DocManager CA Desktop

**Professional Document Management System for Chartered Accountants**

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com)
[![Python](https://img.shields.io/badge/python-3.14.2-blue.svg)](https://python.org)
[![React](https://img.shields.io/badge/react-18-blue.svg)](https://react.dev)
[![License](https://img.shields.io/badge/license-proprietary-red.svg)](LICENSE)

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)
- [Support](#support)

---

## 🎯 Overview

DocManager CA Desktop is a **complete document management solution** designed specifically for Chartered Accountants. It runs entirely on your local computer, ensuring maximum security and data privacy while providing powerful features for client management, document organization, and automated reminders.

### Why DocManager?

✅ **Offline-First Architecture** - All data stays on your computer  
✅ **Professional Client Portal** - Clients access documents securely  
✅ **Automated Reminders** - Multi-client email/WhatsApp reminders  
✅ **Public Website** - Professional CA website with your branding  
✅ **Zero Cloud Dependency** - Complete control over your data  
✅ **Easy to Use** - Modern, intuitive interface

---

## ✨ Features

### 👨‍💼 For Chartered Accountants

#### Client Management
- **Complete client database** with profiles and contact information
- **Client types** - Individual, Business, or Unspecified
- **Bulk operations** - Manage multiple clients efficiently
- **Client directory** - Automatic folder creation for each client

#### Document Management
- **Organized storage** - Documents grouped by client and year
- **Multiple upload methods** - Single file, multiple files, or entire folders
- **Supported formats** - PDF, Excel, Word, Images, ZIP
- **Smart browsing** - Navigate by client name with back button
- **Document preview** - Quick view with system default apps
- **Full-text search** - Find documents quickly

#### Enhanced Reminder System
- **Multi-client reminders** - Send to multiple clients at once
- **Multi-document reminders** - Multiple documents per reminder
- **Document types** - ITR, GST, PAN, TDS, Audit, Financial Statements
- **Email integration** - Professional automated emails via Resend
- **WhatsApp support** - Generate WhatsApp message links
- **Year tracking** - Financial year support (e.g., AY 2025-26)
- **Custom instructions** - Add personalized messages

#### Professional Public Website
- **Custom branding** - "Welcome to Dagdiya Associates"
- **CA color scheme** - Professional blue/white design
- **Service showcase** - Display your CA services with icons
- **Client testimonials** - Build trust with reviews
- **Contact information** - Office address, phone, email
- **Responsive design** - Works on all devices

#### Compliance Tracking
- **Deadline monitoring** - Track important compliance dates
- **Document checklists** - Know what's missing
- **Client status** - See compliance at a glance
- **Automated alerts** - Never miss a deadline

### 🔐 For Clients

#### Secure Client Portal
- **Easy login** - Use phone number and password
- **Document access** - View all shared documents
- **Download capability** - Get documents anytime
- **Reminder notifications** - See pending requirements
- **Mobile friendly** - Access from any device

### 🛡️ Security & Technical

- **Local SQLite Database** - Fast, reliable, offline
- **JWT Authentication** - Industry-standard security
- **Password hashing** - bcrypt encryption
- **Secure file storage** - Organized directory structure
- **No external dependencies** - Runs completely offline
- **Professional architecture** - FastAPI + React

---

## 🚀 Quick Start

### One-Command Setup

```bash
# Start everything (first time will install dependencies)
./start.sh
```

### Access URLs

- **CA Dashboard**: http://localhost:5174/ca
- **Client Portal**: http://localhost:5174/portal
- **Public Website**: http://localhost:5174/ca-lokesh-dagdiya
- **API Documentation**: http://localhost:8443/docs

### Default Credentials

**CA Login**:
- Username: `lokesh`
- Password: `lokesh`

**Demo Client**:
- Phone: `9876543210`
- Password: `client123`

⚠️ **Change default passwords immediately after first login!**

---

## 📚 Documentation

Comprehensive guides are available in `docs/guides/`:

| Guide | Description | Link |
|-------|-------------|------|
| **User Guide** | Complete CA user manual | [docs/guides/USER_GUIDE.md](docs/guides/USER_GUIDE.md) |
| **Developer Guide** | Technical documentation | [docs/guides/DEVELOPER_GUIDE.md](docs/guides/DEVELOPER_GUIDE.md) |
| **Deployment Guide** | Production setup | [docs/guides/DEPLOYMENT_GUIDE.md](docs/guides/DEPLOYMENT_GUIDE.md) |

### Quick Links

- **Client Management** - Add, edit, manage clients
- **Document Upload** - Single, multiple, folder uploads
- **Reminders** - Create multi-client/document reminders
- **Public Website** - Setup your professional CA website
- **Client Portal** - Enable client document access

---

## 💻 System Requirements

### Minimum Requirements
- **OS**: Windows 10+, macOS 10.15+, or Linux
- **CPU**: Dual-core processor
- **RAM**: 4 GB
- **Storage**: 20 GB available
- **Browser**: Chrome, Firefox, Safari, or Edge (latest)

### Recommended
- **OS**: Latest stable version
- **CPU**: Quad-core processor
- **RAM**: 8 GB+
- **Storage**: 100 GB+ SSD
- **Network**: For email reminders and client portal access

---

## 📦 Installation

### Step 1: Install Prerequisites

**Python 3.14.2**:
```bash
# macOS (using Homebrew)
brew install python@3.14

# Windows - Download from python.org
# Linux - Use your package manager
```

**Node.js 18+**:
```bash
# macOS
brew install node

# Windows - Download from nodejs.org
# Linux - Use nvm or package manager
```

### Step 2: Clone/Download Application

```bash
git clone <repository-url>
cd DocManager
```

### Step 3: Setup Database

```bash
# Activate Python environment
source ca_desktop/backend/venv/bin/activate  # macOS/Linux
# OR
ca_desktop\backend\venv\Scripts\activate  # Windows

# Initialize database
python scripts/setup_database.py

# Optional: Load demo data
python scripts/setup_demo_data.py
```

### Step 4: Configure Environment

Create `.env` file:
```bash
# Required for email reminders
RESEND_API_KEY=re_your_api_key_here

# Optional configurations
DATABASE_URL=sqlite:///./ca_desktop.db
FRONTEND_URL=http://localhost:5174
```

### Step 5: Start Application

```bash
./start.sh
```

**Detailed installation instructions**: See [Deployment Guide](docs/guides/DEPLOYMENT_GUIDE.md)

---

## 🎓 Usage

### Adding Clients

1. Navigate to **Clients** section
2. Click **"Invite Client"**
3. Fill in client information
4. Set client type (Individual/Business)
5. Create password for client portal access

### Uploading Documents

1. Go to **Documents** section
2. Select client and year
3. Drag & drop files or click to browse
4. Upload single, multiple, or entire folders
5. Documents auto-organized by client

### Creating Reminders

1. Navigate to **Reminders**
2. Click **"Create Reminder"**
3. **Select multiple clients** (checkboxes)
4. **Add documents** with types and years
5. Choose **email/WhatsApp** delivery
6. Add optional instructions
7. Submit (creates N clients × M documents reminders)

### Setting Up Public Website

1. Go to **Profile** section
2. Update firm information
3. Add services (Tax, GST, Audit, etc.)
4. Add testimonials
5. Upload logo and images
6. Share your URL with clients

### Enabling Client Portal

1. Create client account
2. Set portal password
3. Share portal URL: `http://<your-ip>:5174/portal`
4. Provide client with login credentials
5. Client can access documents anytime

**Complete usage instructions**: See [User Guide](docs/guides/USER_GUIDE.md)

---

## 🧪 Testing

### Run All Tests

```bash
# API Tests (all endpoints)
python tests/api/test_api_complete.py

# E2E Workflow Tests (complete user journeys)
python tests/workflows/test_e2e_workflows.py

# Quick System Test
python scripts/test_everything.py
```

### Test Coverage

- ✅ **Authentication** - CA and client login
- ✅ **Client Management** - CRUD operations
- ✅ **Document Operations** - Upload, list, download
- ✅ **Reminders System** - Multi-client/document
- ✅ **CA Profile** - Update, services
- ✅ **Public API** - Website endpoints
- ✅ **Compliance** - Status tracking
- ✅ **Complete Workflows** - Real user scenarios

### Manual Testing Checklist

- [ ] CA login successful
- [ ] Create new client
- [ ] Upload documents (single, multiple, folder)
- [ ] Create multi-client reminder
- [ ] Update CA profile
- [ ] Access public website
- [ ] Client portal login
- [ ] Client document access

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│   Frontend (React + TypeScript)         │
│   Port: 5174                            │
│   - CA Dashboard                        │
│   - Client Portal                       │
│   - Public Website                      │
└────────────┬────────────────────────────┘
             │ REST API (HTTP/JSON)
┌────────────▼────────────────────────────┐
│   Backend (FastAPI + Python)            │
│   Port: 8443                            │
│   - Authentication (JWT)                │
│   - Business Logic                      │
│   - File Operations                     │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│   Database (SQLite)                     │
│   File: ca_desktop.db                   │
│   - Users, Clients                      │
│   - Documents, Reminders                │
│   - CA Profiles, Services               │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│   File Storage (Local Disk)             │
│   Path: data/uploads/                   │
│   Structure: {client_phone}/            │
└─────────────────────────────────────────┘
```

---

## 🔧 Technology Stack

### Backend
- **Python 3.14.2** - Core language
- **FastAPI** - Modern API framework
- **SQLAlchemy** - ORM for database
- **SQLite** - Lightweight database
- **bcrypt** - Password hashing
- **python-jose** - JWT tokens
- **Resend** - Email service

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Fast build tool
- **TanStack Query** - Server state management
- **Tailwind CSS** - Utility-first styling
- **Lucide React** - Modern icons

### Tools
- **Git** - Version control
- **npm** - Package management
- **pytest** - Testing framework

---

## 📁 Project Structure

```
DocManager/
├── ca_desktop/
│   ├── backend/          # FastAPI application
│   │   └── src/
│   │       ├── routers/  # API endpoints
│   │       └── services/ # Business logic
│   └── frontend/         # React application
│       └── src/
│           └── components/  # UI components
├── tests/
│   ├── api/              # API test suite
│   └── workflows/        # E2E test suite
├── scripts/              # Utility scripts
├── docs/
│   └── guides/           # Documentation
├── data/
│   └── uploads/          # Document storage
├── start.sh              # Startup script
├── ca_desktop.db         # SQLite database
└── README.md             # This file
```

---

## 🆘 Support

### Troubleshooting

**Application won't start**:
```bash
# Check ports
lsof -i :5174
lsof -i :8443

# Restart
./start.sh
```

**Database issues**:
```bash
# Reset database
rm ca_desktop.db
python scripts/setup_database.py
```

**Email reminders not working**:
- Check `.env` has valid `RESEND_API_KEY`
- Verify API key at https://resend.com/

**Client portal not accessible**:
- Verify CA computer IP address
- Configure firewall (ports 5174, 8443)
- Ensure same network

### Getting Help

1. Check [User Guide](docs/guides/USER_GUIDE.md)
2. Review [Troubleshooting Section](docs/guides/DEPLOYMENT_GUIDE.md#troubleshooting)
3. Check logs in `logs/` directory
4. Contact system administrator

---

## 📝 License

Proprietary software. All rights reserved.

---

## 🎯 Version Information

**Current Version**: 1.0.0  
**Release Date**: March 2026  
**Python Version**: 3.14.2  
**Node Version**: 18+

---

## 🚀 What's New in v1.0

- ✅ Complete reminders system with multi-client/document support
- ✅ Professional public website with Dagdiya Associates branding
- ✅ Email integration via Resend API
- ✅ WhatsApp reminder support
- ✅ Enhanced document upload (multiple files, folders)
- ✅ Improved UI with CA color scheme
- ✅ Document type categorization (ITR, GST, PAN, etc.)
- ✅ Comprehensive test suites (API + E2E workflows)
- ✅ Complete documentation (User, Developer, Deployment guides)

---

**DocManager CA Desktop** - Professional Document Management for Chartered Accountants

*Built with ❤️ for CA professionals*
3. ✅ Setup database with demo data
4. ✅ Start backend server on port 8443
5. ✅ Install frontend dependencies
6. ✅ Start frontend server on port 5174

### Access Points

After running `./start.sh`, access the application at:

| Component | URL | Credentials |
|-----------|-----|-------------|
| **CA Login** | http://localhost:5174/ca/login | `lokesh` / `lokesh` |
| **Client Portal** | http://localhost:5174/portal/login | `9876543210` / `client123` |
| **Public Website** | http://localhost:5174/ca-lokesh-dagdiya | (No login required) |
| **API Documentation** | http://localhost:8443/docs | (Interactive Swagger UI) |

---

## 📖 Manual Setup

If you prefer to set up manually or the script doesn't work:

### 1. Backend Setup

```bash
# Navigate to backend directory
cd ca_desktop/backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Go back to root directory
cd ../..

# Setup database with demo data
python scripts/setup_database.py

# Start backend server
cd ca_desktop/backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8443 --reload
```

### 2. Frontend Setup

Open a **new terminal** window:

```bash
# Navigate to frontend directory
cd ca_desktop/frontend

# Install dependencies
npm install

# Create .env file
echo "VITE_API_URL=http://localhost:8443/api/v1" > .env

# Start development server
npm run dev
```

---

## 🏗️ Project Structure

```
DocManager/
├── ca_desktop/
│   ├── backend/                    # FastAPI Backend
│   │   ├── src/
│   │   │   ├── routers/           # API route handlers
│   │   │   │   ├── auth.py        # Authentication
│   │   │   │   ├── clients.py     # Client management
│   │   │   │   ├── documents.py   # Document operations
│   │   │   │   ├── messaging.py   # Messaging system
│   │   │   │   ├── ca_profile.py  # CA profile management
│   │   │   │   └── public.py      # Public website API
│   │   │   ├── models.py          # SQLAlchemy models
│   │   │   ├── schemas.py         # Pydantic schemas
│   │   │   ├── database.py        # Database configuration
│   │   │   ├── config.py          # App configuration
│   │   │   └── main.py            # FastAPI application
│   │   ├── requirements.txt       # Python dependencies
│   │   └── .env                   # Environment variables
│   │
│   └── frontend/                   # React Frontend
│       ├── src/
│       │   ├── components/
│       │   │   ├── ca/            # CA dashboard components
│       │   │   ├── client/        # Client portal components
│       │   │   ├── public/        # Public website components
│       │   │   └── common/        # Shared components
│       │   ├── api/               # API client
│       │   ├── contexts/          # React contexts
│       │   ├── App.tsx            # Main app component
│       │   └── index.css          # Global styles
│       ├── package.json           # Node dependencies
│       └── .env                   # Frontend environment
│
├── scripts/                        # Utility scripts
│   ├── setup_database.py          # Database initialization
│   ├── setup_demo_data.py         # Demo data creation
│   └── test_all_functionality.py  # API testing
│
├── tests/                          # Test suites
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── e2e/                       # End-to-end tests
│
├── .ai/docs/                       # Documentation
│   ├── UI_UPGRADE_SUMMARY.md      # UI improvements
│   ├── BROWSER_TESTING_HANDOFF.md # Testing guide
│   └── START_HERE.md              # Quick start guide
│
├── ca_desktop.db                   # SQLite database
├── start.sh                        # Startup script
└── README.md                       # This file
```

---

## 🔧 Tech Stack

### Backend
- **Python 3.11** - Programming language
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM for database operations
- **SQLite** - Local database
- **Pydantic** - Data validation
- **JWT** - Authentication tokens
- **Uvicorn** - ASGI server

### Frontend
- **React 18** - UI library
- **TypeScript** - Type-safe JavaScript
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Axios** - HTTP client
- **Lucide React** - Icon library

---

## 📚 Usage Guide

### For CA (Admin)

1. **Login** at http://localhost:5174/ca/login
   - Username: `lokesh`
   - Password: `lokesh`

2. **Dashboard** - View overview of clients and documents

3. **Manage Clients**
   - Add new clients individually
   - Bulk upload via CSV
   - Edit client information
   - Deactivate clients

4. **Manage Documents**
   - Upload documents for clients
   - Organize in folders
   - Tag documents
   - Share with clients

5. **Profile & Website**
   - Update firm information
   - Manage services offered
   - Add testimonials
   - Upload media gallery

6. **Messaging**
   - Send messages to clients
   - View message history

### For Clients

1. **Login** at http://localhost:5174/portal/login
   - Phone: `9876543210` (or `9876543211`, `9876543212`, `9876543213`, `9876543214`)
   - Password: `client123`

2. **View Documents**
   - Browse documents shared by CA
   - Download files
   - View document details

3. **Messages**
   - View messages from CA
   - Send replies

---

## 🧪 Testing

### Run All Tests
```bash
python scripts/test_all_functionality.py
```

### Run Specific Test Suites
```bash
# Unit tests
pytest tests/unit/

# Integration tests
pytest tests/integration/

# E2E tests
pytest tests/e2e/
```

---

## 🔐 Security Features

- **Encryption at Rest** - All documents encrypted in database
- **JWT Authentication** - Secure token-based auth
- **CORS Protection** - Configured allowed origins
- **Input Validation** - Pydantic schemas validate all inputs
- **SQL Injection Protection** - SQLAlchemy ORM prevents SQL injection
- **Password Hashing** - Bcrypt for secure password storage
- **Local Storage** - No cloud dependencies

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8443 is in use
lsof -i :8443

# Kill process if needed
kill -9 <PID>

# Reinstall dependencies
cd ca_desktop/backend
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Check if port 5174 is in use
lsof -i :5174

# Clear node_modules and reinstall
cd ca_desktop/frontend
rm -rf node_modules package-lock.json
npm install
```

### Database issues
```bash
# Reset database
rm ca_desktop.db
python scripts/setup_database.py
```

### CORS errors
Check that `ca_desktop/backend/.env` has:
```
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173","http://localhost:5174"]
```

---

## 📝 Demo Data

The system comes with pre-populated demo data:

- **1 CA Admin**: lokesh / lokesh
- **5 Clients**: Phone numbers 9876543210-9876543214, password: client123
- **Sample documents** for each client
- **Services and testimonials** for public website

---

## 📄 License

**Proprietary** - All rights reserved

---

## 🤝 Support

For issues or questions:
- Check documentation in `.ai/docs/`
- Review API docs at http://localhost:8443/docs
- Check logs in `logs/` directory

---

## 🎨 UI Features

The application features a modern, professional UI with:
- ✨ Gradient backgrounds
- 💫 Smooth animations
- 🎯 Hover effects
- 📱 Responsive design
- 🎨 Professional color scheme (blue-indigo-purple)

See `.ai/docs/UI_UPGRADE_SUMMARY.md` for details.

---

**Built with ❤️ for Chartered Accountants**
