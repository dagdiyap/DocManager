# Developer Guide

## Development Setup

See `START_HERE.md` and `README.md` for initial setup instructions.

## Directory Structure

- `ca_desktop/backend`: FastAPI application.
- `ca_desktop/frontend`: React application (Vite).
- `license_server`: License authority service.
- `shared`: Shared Python library for crypto and utilities.
- `tests`: Integration and End-to-End tests.
- `scripts`: Helper scripts.

## Running Tests

We provide a comprehensive script to run all tests:

```bash
./scripts/run_tests.sh
```

This runs:
1.  Backend Unit & Integration Tests (pytest)
2.  Frontend Unit Tests (vitest)

## Code Quality

We use `ruff` for linting, `black` for formatting, and `mypy` for static type checking.

Run all checks:

```bash
./scripts/lint.sh
```

## Database Migrations

We use Alembic for migrations.

### Creating a new migration

```bash
cd ca_desktop/backend
source ../../venv/bin/activate
alembic revision --autogenerate -m "Description of change"
```

### Applying migrations

```bash
alembic upgrade head
```

## Docker Development

You can run the full stack in Docker containers:

```bash
docker-compose -f docker-compose.full.yml up --build
```

## API Documentation

- CA Backend: http://localhost:8443/docs
- License Server: http://localhost:8000/docs
