📘 SYSTEM DESIGN MANUAL
CA Document Access Platform (Offline-Controlled, No Cloud Server)
1. PURPOSE

Build a document-sharing system for Chartered Accountants (CAs) where:

Client documents remain on the CA’s computer.

No permanent cloud server is used.

The developer’s laptop acts as a periodic license authority.

Clients access documents through a web portal.

CAs use a desktop application with embedded web UI.

Access is controlled through licensing and device binding.

System works mostly offline.

This is a Proof-of-Concept and foundation for future scaling.

2. HIGH-LEVEL ARCHITECTURE
System Components
+--------------------+
| Developer Laptop   |
| (License Server)   |
+---------+----------+
          |
   License Tokens
          |
+---------v----------+
| CA Desktop System  |
| (Main Server)      |
+---------+----------+
          |
   File Streaming
          |
+---------v----------+
| Client Browser     |
+--------------------+

Roles
Component	Role
Developer Laptop	License authority (periodic)
CA Laptop	Main application + file server
Client	Read-only web access

No permanent cloud infrastructure is used.

3. COMPONENT BREAKDOWN
3.1 Developer Laptop (License Authority Server)
Purpose

Acts as a temporary central authority for licensing.

Runs only when developer starts it manually.

Responsibilities

Generate CA accounts

Register device fingerprints

Issue license tokens

Set expiry periods

Disable expired accounts

Maintain CA registry

Technology

FastAPI

SQLite/PostgreSQL (local)

JWT / RSA signing

Admin Web UI

APIs
POST /register_ca
POST /validate_device
POST /issue_license
POST /revoke_license
GET  /status

Data Stored
CA_ID
Device_Fingerprint
License_Expiry
Status
Last_Sync


3.2 CA Desktop Application (Main System)
Purpose

Runs permanently on CA computer.

Hosts:

Web UI

Authentication

Document service

Client portal

License validator

This is the core system.

Architecture
Desktop Wrapper App
     |
Docker / Embedded Runtime
     |
FastAPI Backend
     |
Local DB + File System

Responsibilities
A. Folder Management

Scan document folders

Validate structure

Index metadata

B. Authentication

Client login (phone + password)

CA login

Session handling

C. License Enforcement

Store license token

Validate signature

Check expiry

Disable system on failure

D. File Streaming

Serve files on demand

Enforce token validation

No permanent uploads

E. Web UI

CA dashboard

Client management

Document browser

Manual send

Logs

Technology

FastAPI

SQLite

Uvicorn

PyInstaller / Electron Wrapper

HTMX / React UI

Internal Modules
/auth
/license
/files
/clients
/ui
/logs
/sync

Local Database
clients
users
sessions
documents
downloads
licenses
devices
logs

3.3 Client Web Portal
Purpose

Provides read-only access to documents.

Runs on CA system.

Features

Login (phone + password)

Browse years

Browse documents

Download files

View history

Technology

HTML + Tailwind

HTMX / React

Cookie-based sessions

Access Rules

One client = one namespace

No cross-client visibility

Token-validated downloads

4. DOCUMENT ORGANIZATION STANDARD

Mandatory folder structure on CA machine:

ROOT/
  CLIENT_<ID>/
    metadata.json
    FY_2022_23/
      ITR.pdf
      FORM16.pdf
    FY_2023_24/
      GST/
        GSTR1.pdf

Rules

No spaces in IDs

Fixed naming

One client per folder

One year per folder

Agent rejects invalid layout

5. AUTHENTICATION MODEL
5.1 CA Authentication

Handled by Developer Laptop.

Flow:

CA installs app

Generates device fingerprint

Registers with developer

Receives license token

Stores locally

Token validity: 7–30 days.

5.2 Client Authentication

Handled locally.

Username = phone number

Password = hashed

Stored in SQLite

No external services

5.3 Sessions

JWT / Cookies

Local storage

Expiry: configurable

6. LICENSING MODEL
License Token Structure
{
  "ca_id": "CA001",
  "device_id": "HASH123",
  "issued_at": "2026-01-01",
  "expires_at": "2026-01-08",
  "signature": "RSA"
}

Validation

Public key embedded in app

Signature verified locally

Expiry checked

Device ID matched

Enforcement

If invalid:

Disable file service

Disable login

Show license error page

7. DEVICE BINDING
Fingerprint Generation

Combine:

CPU ID
Disk Serial
MAC
Windows SID


Hash using SHA256.

Storage

Stored on:

Developer server

CA local DB

Mismatch → invalidate.

8. FILE ACCESS FLOW
Download Flow
Client → Login
Client → Request File
CA Backend → Validate
CA Backend → Generate Token
Client → Download with Token
CA Backend → Stream File

Token Structure
{
  "client_id": "C001",
  "path": "/FY_2023/ITR.pdf",
  "expiry": 600,
  "nonce": "XYZ",
  "signature": "HMAC"
}

Properties

Single-use

Time-limited

Client-bound

9. WORKFLOWS
9.1 Setup Workflow

Developer runs license server

Generates CA credentials

CA installs app

Registers device

Receives token

Activates

9.2 Document Upload

CA adds files

Agent scans

Updates metadata

Reindexes

9.3 Client Access

Client logs in

Selects year

Selects document

Downloads

9.4 License Renewal

Developer server online

CA syncs

Receives new token

Continues offline

10. PACKAGING & DEPLOYMENT (WINDOWS)
Distribution

Single installer:

CA_DocManager_Setup.exe

Installer Responsibilities

Install runtime

Configure ports

Setup firewall

Register startup

Create shortcut

Runtime

Auto-start on boot

Background service

Opens UI in browser

11. SECURITY MODEL
Implement

Password hashing (bcrypt)

HTTPS (self-signed/local)

Signed tokens

Device binding

Input validation

Rate limiting (basic)

Prevent

Path traversal

Token replay

Brute force

Unauthorized access

12. RESOURCE CONSTRAINTS
Target
Resource	Limit
RAM	< 300MB
CPU	< 10% idle
Disk	Minimal
Strategy

Streaming only

No caching files

SQLite

Lazy loading

13. TECH STACK
Backend

Python 3.11

FastAPI

Uvicorn

SQLite

SQLAlchemy

Frontend

HTMX / React

Tailwind

Packaging

PyInstaller

Electron (optional)

Crypto

PyJWT

cryptography

14. DEVELOPMENT PHASES
Phase 1 – POC

Local auth

License sync

Basic UI

Manual upload

Download

Phase 2 – MVP

Device binding

Logs

Notifications

Installer

Phase 3 – Product

Auto updates

WhatsApp

Cloud fallback

Analytics

15. NON-GOALS (v1)

Client uploads

Mobile apps

Cloud backup

AI features

Multi-CA sharing

16. SUCCESS CRITERIA

System is successful if:

CA can install without technical help

Client can download in < 3 clicks

License cannot be bypassed easily

Files never leave CA PC

No cloud dependency

✅ FINAL SUMMARY

This system:

Uses CA PC as server

Uses developer laptop as license authority

Works offline

Protects business model

Is Windows-first

Is scalable later





1. CORE OBJECTIVE

Build a system where:

All client documents remain on the CA’s computer.

No permanent cloud server is used.

A developer laptop acts as a periodic license authority.

Clients access documents through a web portal hosted on CA PC.

Access is controlled through offline license tokens.

System works mostly offline.

CA cannot use the system without valid license.

2. SYSTEM COMPONENTS
A. Developer Laptop (License Server)

Runs manually when needed.

Responsibilities:

Register CA accounts

Register device fingerprints

Issue signed license tokens

Set expiry (7–30 days)

Revoke licenses

Tech:

FastAPI
SQLite/Postgres (local)
JWT / RSA signing

Admin Web UI

APIs:
POST /register_ca
POST /register_device
POST /issue_license
POST /revoke_license
GET  /status

B. CA Desktop Application (Main Server)

Runs permanently on CA Windows machine.

Responsibilities:
Authentication
CA login
Client login (phone + password)
Session handling
License Enforcement
Validate signed license token
Check expiry
Verify device ID
Disable system if invalid
Document Management
Scan folders
Validate structure
Index metadata
No file upload to cloud

File Serving

Token-based downloads

Streaming only

No caching

Web UI

CA dashboard

Client manager

Document browser

Manual file send

Logs

Local Database

SQLite

Tech:

Python 3.11

FastAPI

Uvicorn

SQLite

SQLAlchemy

HTMX or React

PyInstaller wrapper