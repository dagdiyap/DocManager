# DocManager CA Desktop - Developer Guide

**Technical Documentation for Developers**  
**Version**: 1.0  
**Last Updated**: March 2026

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Local Development Setup](#local-development-setup)
5. [Backend Development](#backend-development)
6. [Frontend Development](#frontend-development)
7. [Database Schema](#database-schema)
8. [API Documentation](#api-documentation)
9. [Testing](#testing)
10. [Common Tasks](#common-tasks)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

DocManager is an offline-first desktop application for Chartered Accountants with:

- **Backend**: FastAPI REST API server
- **Frontend**: React SPA with TypeScript
- **Database**: SQLite (local file-based)
- **Architecture**: Client-Server on localhost

```
┌─────────────────────────────────────────────┐
│           Frontend (React + TS)             │
│         http://localhost:5174               │
└──────────────────┬──────────────────────────┘
                   │ HTTP/REST
┌──────────────────▼──────────────────────────┐
│       Backend (FastAPI + Python)            │
│         http://localhost:8443               │
└──────────────────┬──────────────────────────┘
                   │
┌──────────────────▼──────────────────────────┐
│      Database (SQLite)                      │
│         ca_desktop.db                       │
└─────────────────────────────────────────────┘
```

---

## Technology Stack

### Backend
- **Python 3.14.2**
- **FastAPI** - Modern web framework
- **SQLAlchemy** - ORM
- **SQLite** - Database
- **Pydantic** - Data validation
- **bcrypt** - Password hashing
- **python-jose** - JWT tokens
- **Resend** - Email service

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool
- **TanStack Query** - Server state
- **Tailwind CSS** - Styling
- **Lucide React** - Icons
- **React Hot Toast** - Notifications

### Shared
- **Cryptography** - Encryption utilities
- **Validators** - Common validation logic

---

## Project Structure

```
DocManager/
├── ca_desktop/
│   ├── backend/
│   │   ├── src/
│   │   │   ├── main.py              # FastAPI app entry
│   │   │   ├── config.py            # Configuration
│   │   │   ├── database.py          # DB connection
│   │   │   ├── models.py            # SQLAlchemy models
│   │   │   ├── schemas.py           # Pydantic schemas
│   │   │   ├── dependencies.py      # Auth dependencies
│   │   │   ├── routers/             # API endpoints
│   │   │   │   ├── auth.py          # Authentication
│   │   │   │   ├── clients.py       # Client management
│   │   │   │   ├── documents.py     # Document operations
│   │   │   │   ├── reminders_v2.py  # Enhanced reminders
│   │   │   │   ├── ca_profile.py    # CA profile
│   │   │   │   ├── public.py        # Public website API
│   │   │   │   └── compliance.py    # Compliance tracking
│   │   │   ├── services/            # Business logic
│   │   │   │   ├── email_service.py
│   │   │   │   └── reminder_service.py
│   │   │   └── modules/             # Additional modules
│   │   ├── venv/                    # Python virtual env
│   │   └── requirements.txt
│   │
│   └── frontend/
│       ├── src/
│       │   ├── App.tsx              # Main app component
│       │   ├── main.tsx             # Entry point
│       │   ├── api/
│       │   │   └── index.ts         # API client
│       │   ├── contexts/
│       │   │   └── AuthContext.tsx  # Auth state
│       │   ├── components/
│       │   │   ├── ca/              # CA dashboard components
│       │   │   ├── client/          # Client portal components
│       │   │   └── public/          # Public website components
│       │   └── pages/               # Page components
│       ├── package.json
│       └── vite.config.ts
│
├── shared/                          # Shared utilities
│   ├── crypto/                      # Encryption utilities
│   └── utils/                       # Common utilities
│
├── scripts/                         # Utility scripts
│   ├── setup_database.py            # Initialize DB
│   ├── setup_demo_data.py           # Demo data
│   └── test_everything.py           # Quick tests
│
├── tests/                           # Test suites
│   ├── api/                         # API tests
│   │   └── test_api_complete.py
│   └── workflows/                   # E2E workflow tests
│       └── test_e2e_workflows.py
│
├── docs/                            # Documentation
│   └── guides/
│       ├── USER_GUIDE.md
│       ├── DEVELOPER_GUIDE.md
│       └── DEPLOYMENT_GUIDE.md
│
├── data/                            # Data directory
│   └── uploads/                     # Client documents
│
├── logs/                            # Application logs
├── ca_desktop.db                    # SQLite database
├── start.sh                         # Startup script
└── README.md                        # Main documentation
```

---

## Local Development Setup

### Prerequisites

1. **Python 3.14.2** (or compatible version)
2. **Node.js 18+** and npm
3. **Git**
4. Terminal/Command Line

### Initial Setup

```bash
# 1. Clone repository
git clone <repository-url>
cd DocManager

# 2. Setup backend
cd ca_desktop/backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt

# 3. Setup frontend
cd ../frontend
npm install

# 4. Setup database
cd ../..
source ca_desktop/backend/venv/bin/activate
python scripts/setup_database.py
python scripts/setup_demo_data.py

# 5. Configure environment
cp .env.example .env
# Edit .env and add RESEND_API_KEY for email functionality
```

### Environment Variables

Create `.env` file in project root:

```bash
# Email Service (for reminders)
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxxxxxxx

# Database (optional, defaults to ca_desktop.db)
DATABASE_URL=sqlite:///./ca_desktop.db

# JWT Secret (optional, auto-generated if not set)
SECRET_KEY=your-secret-key-here

# CORS (optional)
FRONTEND_URL=http://localhost:5174
```

### Running Development Servers

#### Option 1: Using start script (Recommended)
```bash
./start.sh
```

This starts both backend and frontend concurrently.

#### Option 2: Manual start

**Terminal 1 - Backend:**
```bash
cd ca_desktop/backend
source venv/bin/activate
uvicorn src.main:app --host 0.0.0.0 --port 8443 --reload
```

**Terminal 2 - Frontend:**
```bash
cd ca_desktop/frontend
npm run dev
```

### Verify Setup

1. **Backend**: http://localhost:8443/docs (API documentation)
2. **Frontend**: http://localhost:5174 (Application)
3. **Health Check**: http://localhost:8443/api/v1/health

---

## Backend Development

### Project Structure

```
backend/src/
├── main.py              # FastAPI app, CORS, routers
├── config.py            # Settings, environment vars
├── database.py          # SQLAlchemy setup
├── models.py            # Database models
├── schemas.py           # Pydantic schemas
├── dependencies.py      # Auth, DB dependencies
├── routers/             # API endpoints
└── services/            # Business logic
```

### Adding a New API Endpoint

1. **Create/Update Model** (`models.py`):
```python
class NewModel(Base):
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

2. **Create Schema** (`schemas.py`):
```python
class NewModelBase(BaseModel):
    name: str

class NewModelCreate(NewModelBase):
    pass

class NewModel(NewModelBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True
```

3. **Create Router** (`routers/new_router.py`):
```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..dependencies import get_current_user, get_db

router = APIRouter(prefix="/new", tags=["new"])

@router.get("/")
def list_items(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    items = db.query(models.NewModel).all()
    return items

@router.post("/")
def create_item(
    item: schemas.NewModelCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    db_item = models.NewModel(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
```

4. **Register Router** (`main.py`):
```python
from .routers import new_router

app.include_router(new_router.router, prefix="/api/v1")
```

### Database Migrations

For schema changes:

```bash
# 1. Update models.py
# 2. Delete database (development only)
rm ca_desktop.db

# 3. Recreate
python scripts/setup_database.py
```

**Production**: Use Alembic for migrations (not implemented yet)

### Authentication

Uses JWT tokens. Protected endpoints:

```python
from ..dependencies import get_current_user

@router.get("/protected")
def protected_route(current_user: dict = Depends(get_current_user)):
    # current_user contains: user_id, username, user_type
    return {"message": f"Hello {current_user['username']}"}
```

### Testing Backend

```bash
# Run API tests
python tests/api/test_api_complete.py

# Manual testing via API docs
# Open http://localhost:8443/docs
# Use "Authorize" button with token
```

---

## Frontend Development

### Project Structure

```
frontend/src/
├── App.tsx                    # Main app, routing
├── main.tsx                   # Entry point
├── index.css                  # Global styles
├── api/
│   └── index.ts               # API client with axios
├── contexts/
│   └── AuthContext.tsx        # Authentication state
├── components/
│   ├── ca/                    # CA dashboard
│   │   ├── ClientList.tsx
│   │   ├── DocumentBrowser.tsx
│   │   ├── DocumentUpload.tsx
│   │   ├── ReminderManagement.tsx
│   │   └── CAProfile.tsx
│   ├── client/                # Client portal
│   │   └── ClientDashboard.tsx
│   └── public/                # Public website
│       └── PublicWebsite.tsx
└── pages/
    ├── CALogin.tsx
    ├── ClientLogin.tsx
    └── CADashboard.tsx
```

### Adding a New Component

1. **Create Component**:
```typescript
// components/ca/NewComponent.tsx
import { useState } from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { api } from '../../api'

export default function NewComponent() {
    const [data, setData] = useState([])
    
    const { data: items, isLoading } = useQuery({
        queryKey: ['items'],
        queryFn: () => api.get('/new').then(res => res.data)
    })
    
    return (
        <div className="p-6">
            <h2>New Component</h2>
            {/* Your UI */}
        </div>
    )
}
```

2. **Add to Router** (`App.tsx`):
```typescript
import NewComponent from './components/ca/NewComponent'

// In Routes:
<Route path="/ca/new" element={<NewComponent />} />
```

### API Integration

Add API methods to `api/index.ts`:

```typescript
export const newApi = {
    list: () => api.get('/new'),
    create: (data: any) => api.post('/new', data),
    update: (id: number, data: any) => api.patch(`/new/${id}`, data),
    delete: (id: number) => api.delete(`/new/${id}`)
}
```

### State Management

- **Global Auth State**: `AuthContext.tsx`
- **Server State**: TanStack Query
- **Local State**: React `useState`

### Styling

Uses **Tailwind CSS**:

```tsx
<button className="bg-blue-600 text-white px-4 py-2 rounded-xl hover:bg-blue-700 transition-all">
    Click Me
</button>
```

### Icons

Uses **Lucide React**:

```tsx
import { Upload, Download, Trash2 } from 'lucide-react'

<Upload size={20} className="text-blue-600" />
```

---

## Database Schema

### Core Tables

#### users
- `id` (PK)
- `username`
- `password_hash`
- `user_type` (ca, client)
- `display_name`
- `created_at`

#### clients
- `id` (PK)
- `ca_id` (FK → users.id)
- `name`
- `phone_number` (unique)
- `email`
- `client_type` (individual, business, unspecified)
- `password_hash`
- `created_at`

#### documents
- `id` (PK)
- `client_phone` (FK → clients.phone_number)
- `filename`
- `file_path`
- `file_size`
- `year`
- `uploaded_at`

#### reminders
- `id` (PK)
- `client_phone` (FK → clients.phone_number)
- `document_name`
- `document_type` (ITR, GST, etc.)
- `document_year`
- `reminder_date`
- `message`
- `send_via_email`
- `send_via_whatsapp`
- `email_sent`
- `whatsapp_sent`
- `created_at`

#### ca_profiles
- `id` (PK)
- `user_id` (FK → users.id)
- `firm_name`
- `professional_bio`
- `phone_number`
- `email`
- `address`
- `website_url`
- `linkedin_url`

---

## API Documentation

### Authentication

#### POST `/api/v1/auth/login`
CA login
```json
// Request (form-data)
{
  "username": "lokesh",
  "password": "lokesh"
}

// Response
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

#### POST `/api/v1/auth/client-login`
Client login
```json
// Request (form-data)
{
  "username": "9876543210",
  "password": "client123"
}
```

### Clients

#### GET `/api/v1/clients/`
List all clients (requires CA auth)

#### POST `/api/v1/clients/`
Create new client
```json
{
  "name": "John Doe",
  "phone_number": "9876543210",
  "email": "john@example.com",
  "client_type": "individual",
  "password": "securepass"
}
```

#### GET `/api/v1/clients/{phone}`
Get client details

#### PATCH `/api/v1/clients/{phone}`
Update client

### Documents

#### POST `/api/v1/documents/upload`
Upload document (multipart/form-data)
```
file: <file>
client_phone: "9876543210"
year: "2025"
```

#### GET `/api/v1/documents/`
List documents

#### GET `/api/v1/documents/download-token/{doc_id}`
Get download token

### Reminders (v2)

#### GET `/api/v1/reminders/document-types`
Get available document types

#### POST `/api/v1/reminders/`
Create reminders
```json
{
  "client_phones": ["9876543210", "9876543211"],
  "document_names": ["ITR Filing", "GST Return"],
  "document_types": ["ITR", "GST_GSTR3B"],
  "document_years": ["2025-26", "2026"],
  "reminder_date": "2026-04-30T10:00:00",
  "general_instructions": "Please submit before deadline",
  "send_via_email": true,
  "send_via_whatsapp": false
}
```

#### GET `/api/v1/reminders/`
List reminders (with optional filters)

### Full API Documentation
Visit: http://localhost:8443/docs (when backend is running)

---

## Testing

### API Tests

Test all backend endpoints:
```bash
python tests/api/test_api_complete.py
```

**Tests**:
- Authentication (CA & Client)
- Client Management
- Document Upload & Download
- Reminders System
- CA Profile
- Public API
- Compliance
- Health Check

### E2E Workflow Tests

Test complete user workflows:
```bash
python tests/workflows/test_e2e_workflows.py
```

**Workflows**:
1. New Client Onboarding
2. Document Upload & Management
3. Multi-Client Reminder System
4. Client Portal Access
5. CA Profile & Public Website
6. Compliance Tracking
7. Complete Tax Filing Season

### Manual Testing

1. **Start application**: `./start.sh`
2. **Test CA Dashboard**: http://localhost:5174/ca
3. **Test Client Portal**: http://localhost:5174/portal
4. **Test Public Website**: http://localhost:5174/ca-lokesh-dagdiya

---

## Common Tasks

### Add New Document Type

1. Update `shared/utils/constants.py`:
```python
ALLOWED_DOCUMENT_TYPES = [
    "ITR", "GST_GSTR1", "GST_GSTR3B", "PAN_CARD",
    "NEW_TYPE"  # Add here
]
```

2. Update frontend dropdown in `ReminderManagement.tsx`

### Change Port Numbers

**Backend**: Edit `start.sh` or run manually:
```bash
uvicorn src.main:app --port 9000
```

**Frontend**: Edit `vite.config.ts`:
```typescript
server: {
  port: 3000
}
```

### Reset Database

```bash
rm ca_desktop.db
python scripts/setup_database.py
python scripts/setup_demo_data.py
```

### Add Demo Data

Edit `scripts/setup_demo_data.py` and run:
```bash
python scripts/setup_demo_data.py
```

### Export/Import Database

```bash
# Export
sqlite3 ca_desktop.db .dump > backup.sql

# Import
sqlite3 new_ca_desktop.db < backup.sql
```

---

## Troubleshooting

### Backend Won't Start

**Check Python version**:
```bash
python --version  # Should be 3.14.2 or compatible
```

**Check dependencies**:
```bash
pip install -r requirements.txt
```

**Check port**:
```bash
lsof -i :8443  # Kill process if needed
```

### Frontend Won't Start

**Clear cache**:
```bash
rm -rf node_modules package-lock.json
npm install
```

**Check Node version**:
```bash
node --version  # Should be 18+
```

### Database Errors

**Locked database**:
```bash
# Stop all processes, then:
rm ca_desktop.db-wal ca_desktop.db-shm
```

**Schema errors**:
```bash
# Recreate database
rm ca_desktop.db
python scripts/setup_database.py
```

### CORS Errors

Check `main.py` CORS configuration:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Import Errors

**Backend**:
```bash
# Ensure in virtual environment
source ca_desktop/backend/venv/bin/activate

# Check PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

---

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Docstrings for functions

### TypeScript
- Use TypeScript strict mode
- Proper type definitions
- Functional components with hooks

### Naming Conventions
- **Python**: `snake_case`
- **TypeScript**: `camelCase` for variables, `PascalCase` for components
- **Files**: Match content (e.g., `UserProfile.tsx`)

---

## Contributing

1. Create feature branch
2. Make changes
3. Test thoroughly
4. Create pull request
5. Code review

---

## Additional Resources

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **React Docs**: https://react.dev/
- **SQLAlchemy Docs**: https://docs.sqlalchemy.org/
- **Tailwind CSS**: https://tailwindcss.com/docs

---

**DocManager CA Desktop** - Developer Documentation

*For support, refer to the troubleshooting section or contact the development team.*
