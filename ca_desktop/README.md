# CA Desktop Application

Main application that runs on CA's Windows PC. Serves documents to clients and manages authentication, file streaming, and messaging.

## Features

- Client authentication (phone number + password)
- Document scanning and indexing
- Secure file streaming with token validation
- Messaging system (CA → Client)
- Manual file sharing
- License validation
- Remote support client
- Web-based UI for CA and clients

## Quick Start

### Development Setup

```bash
cd ca_desktop

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate
pip install -e .[dev]

# Copy environment file
cp .env.example .env

# Run migrations
alembic upgrade head

# Start backend
uvicorn src.main:app --reload --port 8443

# Frontend setup (in new terminal)
cd ../frontend
npm install
npm run dev
```

## Configuration

Edit `.env` file:

```env
# Database
DATABASE_URL=sqlite:///./ca_desktop.db

# License Server
LICENSE_SERVER_URL=http://localhost:8000

# Document Storage
DOCUMENTS_ROOT=documents/
SHARED_FILES_ROOT=shared_files/

# Server
PORT=8443
ENABLE_HTTPS=true
```

## Folder Structure

Documents must follow this structure:

```
documents/
  {phone_number}/
    {year}/
      {document_type}.pdf
```

Example:
```
documents/
  9876543210/
    2024/
      ITR.pdf
      GST_GSTR1.pdf
      FORM16.pdf
    2023/
      ITR.pdf
```

Manually shared files:
```
shared_files/
  9876543210/
    Notice_Jan2024.pdf
```

## API Endpoints

### CA Dashboard
- `GET /api/v1/ca/dashboard` - Dashboard stats
- `GET /api/v1/ca/clients` - List clients
- `POST /api/v1/ca/clients` - Add client
- `POST /api/v1/ca/messages` - Send message
- `POST /api/v1/ca/shared-files` - Upload shared file

### Client Portal
- `POST /api/v1/portal/login` - Client login
- `GET /api/v1/portal/documents` - List documents
- `GET /api/v1/portal/messages` - Get messages
- `GET /api/v1/portal/shared-files` - Get shared files
- `GET /api/v1/files/download/{token}` - Download file

## Testing

```bash
# Backend tests
cd backend
pytest --cov

# Frontend tests
cd frontend
npm run test
```

## Building for Production

See [installer/README.md](../installer/README.md) for PyInstaller and Windows installer build instructions.

## Security

- All passwords hashed with bcrypt
- Download tokens are single-use HMAC
- HTTPS with self-signed certificates
- Rate limiting on login endpoints
- Path traversal prevention
- Input validation on all endpoints
