# Administration Guide

This guide is for System Administrators managing the CA Document Manager infrastructure.

## 1. System Architecture

The system consists of:
- **License Server**: PostgreSQL-backed authority (runs on cloud/server).
- **CA Desktop**: SQLite-backed local application (runs on CA's PC).
- **Frontend**: React application serving both CA and Client interfaces.

## 2. Database Management

### CA Desktop (SQLite)
- **Location**: `ca_desktop/backend/data/ca_desktop.db`
- **Backup**: Simply copy this file to a secure backup location.
- **Reset**: Delete the file to reset the application (Warning: All metadata will be lost).

### License Server (PostgreSQL)
- **Backup**: Use `pg_dump` to backup the `license_server` database.
- **Restore**: Use `psql` to restore from backup.

## 3. Configuration

### Environment Variables
Located in `.env` files in respective backend folders.

**CA Desktop Backend:**
- `SECRET_KEY`: Used for JWT signing. **Keep this secret.**
- `CA_DATABASE_URL`: Connection string for SQLite.
- `DOCUMENTS_ROOT`: Path to document storage.

**License Server:**
- `DATABASE_URL`: Connection string for PostgreSQL.
- `SECRET_KEY`: Used for signing license tokens.

## 4. Troubleshooting

### Application Won't Start
1.  Check if ports are in use (8000, 8443, 5173, 5174).
2.  Check logs in `logs/` directory.
3.  Ensure database files/services are accessible.

### License Issues
- If "Invalid License" appears:
  1.  Check system time (clock skew can invalidate tokens).
  2.  Verify RSA keys match between License Server and Desktop.
  3.  Re-issue a new license token from the Admin UI.

### File Permission Errors
- Ensure the user running the application has read/write access to the `documents/` and `data/` directories.

## 5. Updates & Maintenance

### Database Migrations
When updating the application code:
```bash
cd ca_desktop/backend
alembic upgrade head
```

### Log Rotation
- Logs are automatically rotated.
- Check `ca_desktop/backend/logs/` for archived logs.
