# CA Document Manager

A document-sharing system for Chartered Accountants (CAs) where client documents remain on the CA's computer with no permanent cloud server dependency.

## 🎯 Overview

This system enables CAs to securely share documents with their clients through a web portal while maintaining complete control over their data. The system operates primarily offline with periodic license validation.

## 🏗️ Architecture

- **License Server** (Developer Laptop): Periodic license authority running PostgreSQL
- **CA Desktop App** (Windows): Main application serving documents with embedded web UI
- **Client Portal**: Web-based read-only access for clients

## 📁 Project Structure

```
DocManager/
├── license_server/        # License authority server (FastAPI + PostgreSQL)
├── ca_desktop/           # CA desktop application (FastAPI + React)
│   ├── backend/          # Python backend
│   └── frontend/         # React frontend
├── shared/               # Shared utilities (crypto, validators)
├── tests/                # Integration and E2E tests
├── docs/                 # Documentation
└── .github/              # CI/CD workflows
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### Development Setup

```bash
# Clone the repository
git clone <repository-url>
cd DocManager

# Setup License Server
cd license_server
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
docker-compose up -d  # Start PostgreSQL

# Setup CA Desktop Backend
cd ../ca_desktop/backend
python -m venv venv
source venv/bin/activate
pip install -e .

# Setup CA Desktop Frontend
cd ../frontend
npm install

# Run tests
pytest
npm test
```

## 🛠️ Technology Stack

- **Backend**: Python 3.11, FastAPI, SQLAlchemy, SQLite/PostgreSQL
- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Packaging**: PyInstaller, Inno Setup (Windows installer)
- **Testing**: pytest, Playwright, Vitest
- **CI/CD**: GitHub Actions

## 📖 Documentation

- [Implementation Plan](docs/implementation_plan.md)
- [Architecture Overview](architecture.md)
- [API Documentation](docs/api/)
- [User Guides](docs/user_guides/)
- [Development Setup](docs/developer/development_setup.md)

## 🔐 Security

- RSA-signed license tokens
- Device fingerprinting
- HTTPS (self-signed certificates)
- HMAC-signed download tokens
- Password hashing with bcrypt
- Rate limiting and input validation

## 📝 License

Proprietary - All rights reserved

## 👥 Authors

- Developer: [Your Name]

## 🗺️ Roadmap

- [x] Phase 1: Planning & Architecture
- [🔄] Phase 2: Project Setup
- [ ] Phase 3: Core Infrastructure
- [ ] Phase 4: License Server
- [ ] Phase 5: CA Desktop Backend
- [ ] Phase 6: CA Desktop Frontend
- [ ] Phase 7: Client Portal
- [ ] Phase 8-13: Monitoring, Security, Packaging, Testing, Documentation, Deployment

See [task.md](.gemini/antigravity/brain/fbea9053-3bf1-403d-bdf0-5510becccd0f/task.md) for detailed task breakdown.
