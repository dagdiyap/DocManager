# Docker Deployment Guide

This guide describes how to deploy the CA Document Manager system using Docker Compose.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+

## Architecture

The system consists of the following containers:

1.  **License Server Database (`ls-db`)**: PostgreSQL 15 database for the license server.
2.  **License Server Backend (`ls-backend`)**: FastAPI application for license management.
3.  **License Server UI (`ls-ui`)**: React frontend for license administration.
4.  **CA Desktop Backend (`ca-backend`)**: FastAPI application for document management.
5.  **CA Desktop UI (`ca-ui`)**: React frontend for CA and Client portals.

## Quick Start (Full Ecosystem)

To start all services:

```bash
docker-compose -f docker-compose.full.yml up -d --build
```

Access the services:
- License Admin UI: http://localhost:5173
- CA Desktop UI: http://localhost:5174
- License API: http://localhost:8000/docs
- CA Desktop API: http://localhost:8443/docs

## Production Configuration

For production deployment, you should override the default environment variables. Create a `.env` file or modify `docker-compose.full.yml`:

```yaml
services:
  ls-backend:
    environment:
      - SECRET_KEY=your_strong_production_secret_key
      - POSTGRES_PASSWORD=your_strong_db_password
  
  ca-backend:
    environment:
      - SECRET_KEY=your_strong_production_secret_key
```

## Data Persistence

Volumes are defined to persist data:

- `ls_postgres_data`: License server database data.
- `ca_backend_data`: CA desktop SQLite database.
- `ca_backend_docs`: Document storage.
- `ca_backend_shared`: Shared files storage.

## Logs

To view logs:

```bash
docker-compose -f docker-compose.full.yml logs -f
```

To view logs for a specific service:

```bash
docker-compose -f docker-compose.full.yml logs -f ca-backend
```
