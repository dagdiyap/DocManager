# DocManager — Comprehensive Implementation Plan (TASK.md)

## Overview
Bring DocManager from its current partially-implemented state to a production-ready MVP, then complete Phase 2 features. Each phase below is ordered by dependency and priority. A feature is **complete only when its tests pass**.

---

## Phase 0: Critical Bug Fixes & Foundation (Priority: CRITICAL)

### 0.1 Fix Frontend Compilation Bugs
- [ ] Fix `AuthContext.tsx`: `json.parse` → `JSON.parse`, `json.stringify` → `JSON.stringify`
- [ ] Fix `AuthContext.tsx`: `isLoading: bool` → `isLoading: boolean`
- [ ] Fix `MessagingInterface.tsx`: Add missing `MessageSquare` import from lucide-react
- [ ] Fix `DocumentBrowser.tsx`: `file.filename` → `file.file_name` (match backend schema)

### 0.2 Fix Backend Runtime Bugs
- [ ] Fix `Document.tags.contains(tag)` usage in `compliance.py`, `reminders.py`, `documents.py` — replace with proper many-to-many join query
- [ ] Fix `current_user.get("id")` → `current_user.get("user_id")` in `reminders.py` and `ca_profile.py`
- [ ] Fix duplicate `PATCH /clients/{client_phone}` route conflict between `compliance.py` and `clients.py` — remove from `compliance.py` or merge
- [ ] Fix `test_phase2_comprehensive.py`: `from shared.crypto import get_password_hash` → `from ca_desktop.backend.src.dependencies import get_password_hash`
- [ ] Fix `test_phase2_comprehensive.py`: Remove hardcoded `/Users/pdagdiya/DocManager` sys.path — use relative path from conftest

### 0.3 Environment & Config Foundation
- [ ] Create `.env` file from `.env.example` with valid `CA_SECRET_KEY` for local dev
- [ ] Remove MVP-irrelevant config fields: `license_server_url`, `license_server_ws_url`, `support_mode_enabled`, `support_session_timeout_minutes`
- [ ] Add `CA_SECRET_KEY` validation alias fix (currently `validation_alias="CA_SECRET_KEY"` but `.env.example` uses `SECRET_KEY`)
- [ ] Ensure `conftest.py` at project root sets up sys.path correctly for all test files

### 0.4 Add Global Exception Handler
- [ ] Register FastAPI exception handlers for `CADesktopError` subclasses → return structured JSON error responses
- [ ] Add request validation error handler (422) with clear messages

---

## Phase 1: MVP Core Completion (Priority: HIGH)

### 1.1 Multi-Extension Document Scanner
- [ ] Update `scanner.py` line 61: Support `.pdf`, `.xlsx`, `.xls`, `.png`, `.jpg`, `.jpeg`, `.gif`, `.webp`
- [ ] Update `validate_document_type()` to accept mixed-case filenames (current regex requires `^[A-Z0-9_]+$` — too strict for real filenames)
- [ ] Write unit tests for scanner with multiple file types
- [ ] Write unit tests for edge cases (empty dirs, invalid names, nested dirs)

### 1.2 CA User Bootstrap / Registration
- [ ] Add `POST /api/v1/auth/register` endpoint for initial CA user creation (first-run only, disable after first user exists)
- [ ] Add CA Login page frontend component (replace TBD placeholder)
- [ ] Write integration test for CA registration + login flow

### 1.3 Document Upload Endpoint
- [ ] Add `POST /api/v1/documents/upload` — accept file + client_phone + year, save to correct folder structure, index in DB
- [ ] Add file validation: allowed extensions, max size, filename sanitization
- [ ] Add file hash (SHA256) computation on upload
- [ ] Write integration tests for upload (valid file, invalid extension, too large, path traversal attempt)

### 1.4 Shared File Download
- [ ] Add download token generation for shared files (similar to document download)
- [ ] Add `GET /api/v1/messaging/shared-files/download-token/{shared_file_id}` endpoint
- [ ] Add `GET /api/v1/messaging/shared-files/download/{token}` endpoint using FileStreamer with `is_shared=True`
- [ ] Write integration tests

### 1.5 Download Audit Logging
- [ ] Write to `Download` table on every successful file download (documents + shared files)
- [ ] Enforce single-use download tokens (check token in DB before serving)
- [ ] Write unit tests for token reuse prevention

### 1.6 Rate Limiting Middleware
- [ ] Implement simple in-memory rate limiter middleware (per IP)
- [ ] Use `rate_limit_per_minute` from config
- [ ] Write test for rate limit enforcement

### 1.7 Remove License Server Dependencies from MVP
- [ ] Remove `license.py` router file (not mounted but exists)
- [ ] Remove `License` and `Device` models from `models.py` (or mark as deprecated)
- [ ] Remove license-related imports from `main.py` if any remain
- [ ] Remove `SupportClient` module (`modules/support/client.py`)
- [ ] Remove license-related schemas (`LicenseRegister`, `LicenseStatus`) from `schemas.py`
- [ ] Remove license-related exceptions from `exceptions.py`
- [ ] Clean up `DashboardStats` schema (remove `active_licenses` field)
- [ ] Update frontend Dashboard to remove License widget and Support Mode toggle

---

## Phase 2: Frontend Completion (Priority: HIGH)

### 2.1 CA Login Page
- [ ] Build proper CA login form component at `/ca/login`
- [ ] Handle login API call, store token, redirect to `/ca`
- [ ] Add error handling and loading states

### 2.2 Document Upload UI
- [ ] Build file upload component for CA: drag-and-drop or file picker
- [ ] Client selector + year input
- [ ] Progress indicator, success/error feedback
- [ ] Wire to `POST /api/v1/documents/upload`

### 2.3 Client Portal Redesign
- [ ] Replace TBD placeholders in portal routes with real components
- [ ] Year-based document grouping view
- [ ] Shared files section with download buttons
- [ ] Remove Messages tab (per MVP spec) OR keep as simple read-only

### 2.4 Wire Activity Logs to Backend
- [ ] Create `GET /api/v1/audit-logs` endpoint (CA only)
- [ ] Connect `ActivityLogs.tsx` to real API instead of hardcoded data
- [ ] Add pagination

### 2.5 Client Management Enhancements
- [ ] Wire "Add New Client" button to a modal/form
- [ ] Wire "View Documents" action to navigate to filtered document browser
- [ ] Wire "Delete" action to deactivate endpoint
- [ ] Add client creation form with validation

---

## Phase 3: Phase 2 Backend Hardening (Priority: MEDIUM)

### 3.1 Fix & Test Tagging System
- [ ] Fix SQLAlchemy many-to-many queries (replace `.contains()` with proper `.any()` or join)
- [ ] Add seed data migration for default tags
- [ ] Write comprehensive unit tests: regex matching, case insensitivity, multiple tags, confidence scores
- [ ] Write integration tests: auto-tag flow, manual tag CRUD

### 3.2 Fix & Test Compliance System
- [ ] Fix compliance status query (same `.contains()` bug)
- [ ] Add seed data for default compliance rules
- [ ] Write unit tests: salaried/business rules, missing document detection
- [ ] Write integration tests: set client type → check status → verify missing docs

### 3.3 Fix & Test Reminder System
- [ ] Fix `created_by_ca_id` bug (use `user_id` from token)
- [ ] Write unit tests: create, list, update, delete reminders
- [ ] Write integration tests: group send flow, recurring reminders
- [ ] Add reminder notification mechanism (even if just marking as sent for now)

### 3.4 Fix & Test CA Profile System
- [ ] Fix `ca_id` extraction bug (use `user_id` from token)
- [ ] Add file type validation on media upload
- [ ] Write unit tests for profile CRUD
- [ ] Write integration tests: full profile setup with media, services, testimonials

### 3.5 Fix & Test Public API
- [ ] Write integration tests: public profile access, media listing, services, testimonials
- [ ] Verify no auth required on public endpoints
- [ ] Add caching headers for public endpoints

---

## Phase 4: Phase 2 Frontend Features (Priority: MEDIUM)

### 4.1 Compliance Calendar UI
- [ ] Build compliance status dashboard component
- [ ] Show per-client compliance status with required vs present docs
- [ ] Visual indicators (green/red/yellow) for compliance state

### 4.2 Reminder Management UI
- [ ] Build reminder list/calendar view
- [ ] Create reminder form (client selector, type, date, message)
- [ ] Group reminder send interface
- [ ] Mark as sent functionality

### 4.3 CA Profile Setup UI
- [ ] Build profile edit form
- [ ] Media upload (carousel images) with drag-and-drop reordering
- [ ] Services CRUD interface
- [ ] Testimonials CRUD interface

### 4.4 CA Public Website Frontend
- [ ] Create new React project or route group for public website
- [ ] Profile display page
- [ ] Image carousel component
- [ ] Services grid
- [ ] Testimonials section
- [ ] Client portal entry link

---

## Phase 5: Testing & Quality (Priority: HIGH)

### 5.1 Backend Unit Tests (Target: ≥80% coverage)
- [ ] Validators: phone, year, doc type, file path, sanitization
- [ ] Crypto: download tokens (create, verify, expired, wrong secret)
- [ ] Scanner: multi-extension, edge cases
- [ ] Auth: password hashing, token creation/verification

### 5.2 Backend Integration Tests
- [ ] Auth flow: register → login → access protected route → logout
- [ ] Client CRUD: create → list → update → deactivate
- [ ] Document lifecycle: upload → scan → search → download
- [ ] Messaging: send message → list → shared file upload → download
- [ ] Tagging: auto-tag → manual tag → search by tag
- [ ] Compliance: set type → check status → resolve
- [ ] Reminders: create → list → group send → delete
- [ ] CA Profile: create → update → media → services → testimonials
- [ ] Public API: profile → media → services → testimonials

### 5.3 Frontend Tests
- [ ] Setup Vitest + Testing Library
- [ ] Auth context tests
- [ ] Login form tests
- [ ] API module tests (mock axios)
- [ ] Key component render tests

### 5.4 Security Tests
- [ ] Path traversal prevention (documents + shared files)
- [ ] Token expiry enforcement
- [ ] Rate limiting
- [ ] SQL injection prevention (parameterized queries verified)
- [ ] Input validation (phone, year, file names)

### 5.5 Code Quality
- [x] Run `ruff` linter and fix all issues
- [x] Run `mypy` type checker and fix critical issues
- [x] Run `black` formatter
- [ ] Frontend: run `eslint` and `prettier`
- [ ] Frontend: run `tsc --noEmit` type check

---

## Phase 6: Database & DevOps (Priority: MEDIUM)

### 6.1 Alembic Migrations
- [ ] Initialize alembic with current models as baseline
- [ ] Generate initial migration from current models
- [ ] Test migration up/down

### 6.2 Development Scripts
- [ ] Create `scripts/dev.sh` — start backend + frontend with hot reload
- [ ] Create `scripts/seed.sh` — seed DB with sample data (CA user, clients, docs, tags, rules)
- [ ] Update README with accurate setup instructions

### 6.3 Docker Setup
- [ ] Update `Dockerfile` for backend
- [ ] Create `docker-compose.yml` for full local dev (backend + frontend)

---

## Phase 7: Documentation (Priority: LOW)

### 7.1 Developer Documentation
- [ ] Update README.md with current architecture and setup
- [ ] Document API endpoints (or enable Swagger UI properly)
- [ ] Document testing strategy and commands

### 7.2 User Documentation
- [ ] Update CA Workflow Guide to match implemented features
- [ ] Create Client Portal user guide

---

## Execution Order (Recommended)

1. **Phase 0** — Fix critical bugs so codebase is runnable
2. **Phase 1.1–1.3** — Core MVP functionality
3. **Phase 5.1–5.2** — Tests for everything implemented
4. **Phase 1.4–1.7** — Complete MVP feature set
5. **Phase 2.1–2.5** — Frontend completion
6. **Phase 3** — Backend hardening for Phase 2 features
7. **Phase 4** — Phase 2 frontend
8. **Phase 5.3–5.5** — Frontend tests + quality
9. **Phase 6** — DevOps
10. **Phase 7** — Documentation
