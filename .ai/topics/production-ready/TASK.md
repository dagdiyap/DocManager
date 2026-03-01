# DocManager — Production-Ready Implementation Plan

## Overview
Transform DocManager into a production-ready, multi-tenant CA document management system with client invite functionality, WhatsApp/email sharing, and comprehensive testing.

---

## Phase 6: Codebase Cleanup & Foundation

### 6.1 Remove License Server Dependencies
- [x] Remove `ca_desktop/backend/src/routers/license.py`
- [ ] Remove `License` and `Device` models from `models.py`
- [ ] Remove `modules/license/validator.py`
- [ ] Remove `modules/support/client.py`
- [ ] Remove license-related schemas from `schemas.py`
- [ ] Remove license-related exceptions from `exceptions.py`
- [ ] Clean up config: remove `license_server_url`, `license_server_ws_url`, `support_mode_enabled`, `support_session_timeout_minutes`
- [ ] Remove `tests/unit/test_license_validator.py`
- [ ] Remove `tests/integration/test_license_server_api.py`

### 6.2 Remove Dead Code
- [ ] Scan for unused imports across all files
- [ ] Remove commented-out code blocks
- [ ] Remove unused utility functions
- [ ] Remove `AuditLog` and `TaskQueue` models if not used
- [ ] Clean up `Download` model (currently not written to)

### 6.3 Dependency Cleanup
- [ ] Review `requirements.txt` and remove unused packages
- [ ] Add `resend` for email service
- [ ] Add `qrcode` and `pillow` for QR generation
- [ ] Add `python-slugify` for CA slug generation
- [ ] Verify all dependencies are pinned with versions
- [ ] Run `pip-audit` for security vulnerabilities

---

## Phase 7: Production Hardening

### 7.1 Centralized Error Handling
- [ ] Create global exception handler in `main.py` for `CADesktopError` subclasses
- [ ] Add 422 validation error handler with clear messages
- [ ] Add 500 internal server error handler with safe error responses
- [ ] Ensure no stack traces leak to clients in production
- [ ] Add error response schema: `{"error": "...", "detail": "...", "timestamp": "..."}`

### 7.2 Structured Logging Enhancement
- [ ] Verify JSON logging is enabled in production
- [ ] Add request ID to all log entries
- [ ] Log all client creation/deletion events
- [ ] Log all document uploads/downloads
- [ ] Log all authentication attempts (success/failure)
- [ ] Ensure passwords are never logged
- [ ] Add log rotation configuration

### 7.3 Audit Logging
- [ ] Implement `AuditLog` writes for:
  - Client creation/update/deletion
  - Document upload/download/deletion
  - Password changes
  - Login attempts
  - Reminder creation/deletion
  - CA profile updates
- [ ] Add audit log query endpoint for CA: `GET /api/v1/audit-logs`
- [ ] Add filters: date range, action type, client phone

### 7.4 Security Hardening
- [ ] Verify bcrypt password hashing is used (already done)
- [ ] Add password strength validation (min 8 chars, mix of types)
- [ ] Implement CORS properly for production domain
- [ ] Add rate limiting verification (already implemented)
- [ ] Add file upload size limits (max 50MB per file)
- [ ] Add allowed file extensions validation
- [ ] Verify path traversal protection in file operations
- [ ] Add CSRF token for state-changing operations (if needed)

### 7.5 Input Validation
- [ ] Review all Pydantic schemas for proper validation
- [ ] Add phone number format validation (10 digits)
- [ ] Add email format validation
- [ ] Add year format validation (YYYY or YYYY-YY)
- [ ] Add filename sanitization on all uploads
- [ ] Add SQL injection prevention verification (already using ORM)

---

## Phase 8: Multi-Tenant Architecture

### 8.1 Database Schema Changes
- [ ] Add `slug` field to `User` model (unique, indexed, lowercase)
- [ ] Add `display_name` field to `User` model (for public profile)
- [ ] Add migration script for existing CA users
- [ ] Add slug generation utility: `generate_slug(name)` → `"lokesh-dagdiya"`
- [ ] Add slug validation: alphanumeric + hyphens only

### 8.2 CA Slug Management
- [ ] Add `POST /api/v1/auth/register` endpoint:
  - Accept: `username`, `email`, `password`, `display_name`
  - Auto-generate slug from `display_name`
  - Ensure slug uniqueness
  - Return: user object with slug
- [ ] Add `PATCH /api/v1/ca/profile/slug` endpoint:
  - Allow CA to change slug (max 3 times)
  - Validate uniqueness
  - Update all related URLs

### 8.3 Multi-Tenant Routing
- [ ] Add public CA profile endpoint: `GET /api/v1/public/ca/{slug}`
  - Return: CA profile, services, testimonials, media
  - Public access (no auth required)
- [ ] Add client portal endpoint: `GET /api/v1/public/ca/{slug}/portal`
  - Return: portal metadata (name, logo, theme)
  - Used by frontend to customize client login page
- [ ] Add data isolation middleware:
  - Verify client can only access their own CA's data
  - Verify CA can only access their own clients

### 8.4 Client Portal URL Structure
- [ ] Frontend routing: `www.example.com/ca-{slug}/home`
- [ ] Client login: `www.example.com/ca-{slug}/login`
- [ ] Client documents: `www.example.com/ca-{slug}/documents`
- [ ] Client messages: `www.example.com/ca-{slug}/messages`

---

## Phase 9: Client Invite System

### 9.1 Password Generation
- [ ] Create `generate_client_password()` utility:
  - 12 characters
  - Mix of uppercase, lowercase, digits, symbols
  - Cryptographically secure random
- [ ] Store hashed password in DB
- [ ] Return plain password only once (in API response)

### 9.2 Invite Card Data Endpoint
- [ ] Add `POST /api/v1/clients/` enhancement:
  - After client creation, return invite data:
    ```json
    {
      "client": {...},
      "invite": {
        "portal_url": "https://www.example.com/ca-lokesh-dagdiya/home",
        "username": "9876543210",
        "password": "Abc123!@#xyz",
        "qr_code_base64": "data:image/png;base64,...",
        "whatsapp_share_url": "https://wa.me/?text=..."
      }
    }
    ```
- [ ] Add `GET /api/v1/clients/{phone}/invite-card` endpoint:
  - Regenerate invite card (without password)
  - For re-sharing portal link

### 9.3 QR Code Generation
- [ ] Install `qrcode` and `pillow` libraries
- [ ] Create `generate_qr_code(url: str) -> str` utility:
  - Generate QR code image
  - Return base64-encoded PNG
  - Size: 300x300px
  - Error correction: Medium
- [ ] QR code contains: `https://www.example.com/ca-{slug}/home`

### 9.4 WhatsApp Share URL
- [ ] Create `generate_whatsapp_share_url()` utility:
  - Format message:
    ```
    Welcome to [CA Name] Portal!
    
    Portal: https://www.example.com/ca-lokesh-dagdiya/home
    Username: 9876543210
    Password: Abc123!@#xyz
    
    Login to view your documents and messages.
    ```
  - URL encode message
  - Return: `https://wa.me/?text={encoded_message}`
- [ ] Test on desktop (opens WhatsApp Web/Desktop)
- [ ] Test on mobile (opens WhatsApp app)

---

## Phase 10: Email Integration (Resend)

### 10.1 Resend Setup
- [ ] Sign up for Resend account (free tier: 3,000 emails/month)
- [ ] Get API key
- [ ] Add to `.env`: `RESEND_API_KEY=re_...`
- [ ] Add to config: `resend_api_key: str`
- [ ] Install `resend` Python SDK

### 10.2 Email Service Module
- [ ] Create `ca_desktop/backend/src/services/email_service.py`:
  - `send_welcome_email(client_email, client_name, portal_url, username, password, ca_name)`
  - Use Resend API
  - HTML email template
  - Handle errors gracefully (log but don't fail client creation)

### 10.3 Email Template
- [ ] Create HTML email template:
  - Subject: "Welcome to [CA Name] Portal"
  - Body:
    - Welcome message
    - Portal link (button)
    - Username and password (styled box)
    - Instructions to login
    - CA contact info
    - Footer with branding
- [ ] Test email rendering on Gmail, Outlook, mobile

### 10.4 Integration with Client Creation
- [ ] Modify `POST /api/v1/clients/` endpoint:
  - If `email` is provided in request:
    - Send welcome email after client creation
    - Log email send status
  - If `email` is null/empty:
    - Skip email sending
    - Only return invite card data

---

## Phase 11: Frontend - Invite Modal

### 11.1 Invite Modal Component
- [ ] Create `ca_desktop/frontend/src/components/ca/InviteModal.tsx`:
  - Props: `isOpen`, `onClose`, `inviteData`
  - Display:
    - Portal URL with [Copy] button
    - Username with [Copy] button
    - Password with [Copy] button
    - QR code image
    - [Share on WhatsApp] button
    - [Close] button
  - Use Tailwind for styling
  - Responsive design

### 11.2 Copy to Clipboard
- [ ] Implement copy functionality:
  - Use `navigator.clipboard.writeText()`
  - Show toast notification: "Copied!"
  - Handle copy errors gracefully

### 11.3 WhatsApp Share Button
- [ ] Implement WhatsApp share:
  - Use `window.open(whatsappShareUrl, '_blank')`
  - Opens in new tab/window
  - Works on desktop and mobile

### 11.4 Integration with Client Creation
- [ ] Modify `ClientManagement.tsx` (or equivalent):
  - After successful `POST /api/v1/clients/` response:
    - Extract `invite` data
    - Open `InviteModal` with invite data
  - User can copy/share immediately

---

## Phase 12: Frontend - Multi-Tenant Routing

### 12.1 Public CA Profile Page
- [ ] Create `ca_desktop/frontend/src/pages/public/CAProfile.tsx`:
  - Route: `/ca-{slug}`
  - Fetch CA profile from `GET /api/v1/public/ca/{slug}`
  - Display:
    - CA name, logo, bio
    - Services offered
    - Testimonials
    - Contact info
    - [Client Portal Login] button → `/ca-{slug}/login`

### 12.2 Client Portal Login Page
- [ ] Create `ca_desktop/frontend/src/pages/client/CAClientLogin.tsx`:
  - Route: `/ca-{slug}/login`
  - Fetch portal metadata from `GET /api/v1/public/ca/{slug}/portal`
  - Customize page with CA branding
  - Login form: phone + password
  - Call `POST /api/v1/auth/login` with `user_type=client`
  - Redirect to `/ca-{slug}/home` on success

### 12.3 Client Portal Dashboard
- [ ] Update `ClientDashboard.tsx`:
  - Route: `/ca-{slug}/home`
  - Ensure all API calls include CA context
  - Display CA branding in header
  - Show only client's own documents/messages

### 12.4 Data Isolation Verification
- [ ] Add middleware/context to verify:
  - Client can only access their CA's data
  - Client cannot access other CA's clients
  - Client cannot access other clients' documents
- [ ] Add frontend route guards

---

## Phase 13: Comprehensive Testing

### 13.1 Unit Tests - New Features
- [ ] `test_password_generation.py`:
  - Test password strength
  - Test uniqueness
  - Test character distribution
- [ ] `test_qr_code_generation.py`:
  - Test QR code creation
  - Test base64 encoding
  - Test URL encoding
- [ ] `test_whatsapp_share.py`:
  - Test message formatting
  - Test URL encoding
  - Test special characters
- [ ] `test_slug_generation.py`:
  - Test slug creation from names
  - Test uniqueness validation
  - Test special character handling
- [ ] `test_email_service.py`:
  - Mock Resend API
  - Test email sending
  - Test error handling

### 13.2 Integration Tests - Invite System
- [ ] `test_client_invite_flow.py`:
  - Create client with email → verify email sent
  - Create client without email → verify no email sent
  - Verify invite card data returned
  - Verify QR code is valid base64
  - Verify WhatsApp URL is properly encoded

### 13.3 Integration Tests - Multi-Tenant
- [ ] `test_multi_tenant_isolation.py`:
  - Create 2 CAs with different slugs
  - Create clients for each CA
  - Verify Client A cannot access Client B's documents
  - Verify CA A cannot access CA B's clients
  - Test public CA profile access
  - Test client portal login with slug

### 13.4 E2E Workflow Tests
- [ ] `test_ca_workflow.py`:
  - CA registers → creates client → uploads document → sets reminder → shares invite
- [ ] `test_client_workflow.py`:
  - Client receives invite → scans QR → logs in → views documents → downloads file
- [ ] `test_whatsapp_share_workflow.py`:
  - CA creates client → clicks WhatsApp share → verifies link opens

### 13.5 Performance Tests
- [ ] Create `tests/performance/test_load.py`:
  - Use `locust` or `pytest-benchmark`
  - Test concurrent client logins (50 users)
  - Test document upload under load (10 concurrent uploads)
  - Test memory usage during 1000 client creation
  - Measure startup time
  - Measure idle CPU/memory consumption
- [ ] Create Docker-based performance test:
  - `docker-compose -f docker-compose.perf.yml up`
  - Run tests in container
  - Measure resource usage
  - Generate performance report

### 13.6 Security Tests
- [ ] `test_path_traversal.py`:
  - Attempt `../../etc/passwd` in file paths
  - Verify rejection
- [ ] `test_sql_injection.py`:
  - Attempt SQL injection in phone/email fields
  - Verify parameterized queries prevent it
- [ ] `test_data_isolation.py`:
  - Verify client cannot access other client's data via API manipulation
- [ ] `test_rate_limiting.py`:
  - Send 100 requests in 1 minute
  - Verify rate limit kicks in

---

## Phase 14: CA User Guide

### 14.1 Installation Guide
- [ ] Create `docs/CA_USER_GUIDE.md`:
  - System requirements (Windows 10+, 4GB RAM, 10GB disk)
  - Download installer
  - Installation steps
  - First-time setup
  - Creating first CA account

### 14.2 Client Management Guide
- [ ] Document:
  - How to add a new client
  - How to edit client details
  - How to deactivate a client
  - How to search clients
  - How to view client compliance status

### 14.3 Document Management Guide
- [ ] Document:
  - How to upload documents
  - How to categorize documents by year/type
  - How to tag documents
  - How to search documents
  - How to download documents
  - How to delete documents

### 14.4 Invite Sharing Guide
- [ ] Document:
  - How to share portal access via WhatsApp
  - How to share via email
  - How to regenerate invite card
  - How to share QR code
  - How to reset client password

### 14.5 Reminder & Compliance Guide
- [ ] Document:
  - How to set reminders
  - How to view compliance status
  - How to mark documents as compliant
  - How to send group reminders

### 14.6 Activity Logs Guide
- [ ] Document:
  - How to view audit logs
  - How to filter logs by date/action
  - How to export logs

---

## Phase 15: Production Deployment

### 15.1 Docker Build
- [ ] Update `Dockerfile`:
  - Multi-stage build for smaller image
  - Production dependencies only
  - Health check endpoint
  - Non-root user
- [ ] Update `docker-compose.yml`:
  - Production configuration
  - Volume mounts for data persistence
  - Environment variables
  - Restart policy

### 15.2 Environment Configuration
- [ ] Create `.env.production` template:
  - `CA_SECRET_KEY`
  - `CA_DATABASE_URL`
  - `RESEND_API_KEY`
  - `ALLOWED_ORIGINS`
  - `DOCUMENTS_ROOT`
- [ ] Document environment setup

### 15.3 Database Migration
- [ ] Initialize Alembic:
  - `alembic init alembic`
  - Configure `alembic.ini`
  - Create initial migration from current models
- [ ] Test migration up/down
- [ ] Document migration process

### 15.4 Windows Installation Test
- [ ] Build Windows installer (using PyInstaller or similar)
- [ ] Install on fresh Windows laptop
- [ ] Verify:
  - Application starts
  - Database initializes
  - CA can register
  - Client creation works
  - Document upload works
  - WhatsApp share opens correctly
  - Email sending works

### 15.5 Mobile Client Test
- [ ] From personal phone:
  - Scan QR code
  - Verify portal loads
  - Login as client
  - View documents
  - Download document
  - Verify responsive design

### 15.6 Performance Validation
- [ ] On Windows laptop:
  - Measure idle CPU usage (should be <5%)
  - Measure idle memory usage (should be <200MB)
  - Add 100 clients
  - Upload 500 documents
  - Verify no slowdowns
  - Verify no memory leaks

---

## Phase 16: Final Validation

### 16.1 Feature Checklist
- [ ] CA can register and login
- [ ] CA can add/edit/delete clients
- [ ] CA can upload/download/delete documents
- [ ] CA can set reminders
- [ ] CA can view compliance status
- [ ] CA can share invite via WhatsApp
- [ ] CA can share invite via email
- [ ] CA can regenerate invite card
- [ ] Client can scan QR code
- [ ] Client can login to portal
- [ ] Client can view documents
- [ ] Client can download documents
- [ ] Client can view messages
- [ ] Multi-tenant isolation works
- [ ] Audit logs are recorded
- [ ] Rate limiting works
- [ ] All tests pass (unit + integration + E2E)

### 16.2 Security Checklist
- [ ] Passwords are hashed with bcrypt
- [ ] No passwords in logs
- [ ] Path traversal protection verified
- [ ] SQL injection prevention verified
- [ ] Rate limiting verified
- [ ] CORS configured correctly
- [ ] File upload size limits enforced
- [ ] Data isolation verified

### 16.3 Performance Checklist
- [ ] Startup time <10 seconds
- [ ] Idle CPU <5%
- [ ] Idle memory <200MB
- [ ] 50 concurrent logins handled
- [ ] 10 concurrent uploads handled
- [ ] No memory leaks after 1000 operations

### 16.4 Documentation Checklist
- [ ] CA User Guide complete
- [ ] API documentation (Swagger) accessible
- [ ] README.md updated
- [ ] Installation guide complete
- [ ] Troubleshooting guide created

---

## Execution Order

1. **Phase 6** — Cleanup (remove license code, dead code, optimize dependencies)
2. **Phase 7** — Hardening (error handling, logging, audit logs, security)
3. **Phase 8** — Multi-tenant (slug architecture, data isolation)
4. **Phase 9** — Invite system backend (password gen, QR, WhatsApp)
5. **Phase 10** — Email integration (Resend setup, templates)
6. **Phase 11** — Invite modal frontend
7. **Phase 12** — Multi-tenant frontend (public profile, client portal)
8. **Phase 13** — Comprehensive testing (unit, integration, E2E, performance)
9. **Phase 14** — CA User Guide
10. **Phase 15** — Production deployment (Docker, Windows, mobile)
11. **Phase 16** — Final validation (all checklists)

---

## Success Criteria

✅ All 16 phases complete
✅ All tests passing (target: 150+ tests)
✅ Performance benchmarks met
✅ Security audit passed
✅ CA User Guide published
✅ Production deployment successful
✅ Mobile client verification complete
✅ Zero-cost implementation (no paid APIs except Resend free tier)
