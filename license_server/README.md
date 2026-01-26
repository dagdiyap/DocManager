# License Server

License authority server for CA Document Manager. Manages CA registration, device binding, and license token issuance.

## Features

- CA registration and management
- Device fingerprinting and validation
- RSA-signed license token generation
- License revocation
- Remote support and monitoring via WebSocket
- Push .exe updates to CA desktops
- Admin web dashboard

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Copy environment file
cp .env.example .env

# Edit .env and set your passwords and secrets

# Start PostgreSQL and License Server
docker-compose up -d

# View logs
docker-compose logs -f license_server

# Run migrations
docker-compose exec license_server alembic upgrade head
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -e .[dev]

# Start PostgreSQL (via Docker)
docker-compose up -d postgres

# Copy and configure environment
cp .env.example .env

# Run migrations
alembic upgrade head

# Start server
uvicorn src.main:app --reload --port 8000
```

### Frontend Development

```bash
cd ui
npm install
npm run dev
```

## API Endpoints

### License Management
- `POST /api/v1/ca/register` - Register new CA
- `POST /api/v1/license/issue` - Issue license token
- `POST /api/v1/license/revoke` - Revoke license

### Remote Support
- `WS /api/v1/support/connect/{ca_id}` - WebSocket connection
- `GET /api/v1/support/diagnostics/{ca_id}` - Get diagnostics
- `POST /api/v1/support/push_update` - Push .exe update

## Configuration

See `.env.example` for all available configuration options.

Key settings:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing secret
- `PRIVATE_KEY_PATH` - RSA private key location
- `DEFAULT_LICENSE_DAYS` - Default license validity period

## Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov --cov-report=html

# Run specific tests
pytest tests/test_license.py -v
```

## Directory Structure

```
license_server/
├── src/              # Source code
│   ├── routers/      # API endpoints
│   └── support/      # Remote support modules
├── ui/               # Admin dashboard (React)
├── tests/            # Unit tests
├── alembic/          # Database migrations
└── keys/             # RSA key storage (gitignored)
```

## Security

- All license tokens are RSA-signed
- WebSocket connections are TLS-encrypted
- Remote commands require CA approval
- Full audit trail of all actions
- Secrets stored in .env (never committed)
