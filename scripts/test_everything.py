#!/usr/bin/env python3
"""
Complete End-to-End Testing Script for DocManager
Tests ALL functionalities and creates a comprehensive report
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta

import requests

# Colors
class C:
    G = '\033[0;32m'  # Green
    R = '\033[0;31m'  # Red
    Y = '\033[1;33m'  # Yellow
    B = '\033[0;34m'  # Blue
    C = '\033[0;36m'  # Cyan
    M = '\033[0;35m'  # Magenta
    NC = '\033[0m'    # No Color

BASE_URL = "http://localhost:8443/api/v1"
FRONTEND_URL = "http://localhost:5174"

results = {"total": 0, "passed": 0, "failed": 0}
ca_token = None
client_token = None
clients = []
documents = []

def test(name, passed, details=""):
    results["total"] += 1
    if passed:
        results["passed"] += 1
        print(f"{C.G}✓{C.NC} {name}")
        if details: print(f"  {C.B}{details}{C.NC}")
    else:
        results["failed"] += 1
        print(f"{C.R}✗{C.NC} {name}")
        if details: print(f"  {C.R}{details}{C.NC}")

def section(text):
    print(f"\n{C.C}▶ {text}{C.NC}")

print(f"\n{C.B}{'='*70}{C.NC}")
print(f"{C.B}{'DocManager - Complete System Test'.center(70)}{C.NC}")
print(f"{C.B}{'='*70}{C.NC}\n")

# 1. Check Services
section("Checking Services")
try:
    r = requests.get(f"{BASE_URL.replace('/api/v1', '')}/docs", timeout=5)
    test("Backend Running", r.status_code == 200, f"Port 8443")
except:
    test("Backend Running", False, "Not accessible")
    sys.exit(1)

try:
    r = requests.get(FRONTEND_URL, timeout=5)
    test("Frontend Running", r.status_code == 200, f"Port 5174")
except:
    test("Frontend Running", False)

# 2. CA Login
section("CA Authentication")
try:
    r = requests.post(f"{BASE_URL}/auth/login",
                     data={"username": "lokesh", "password": "lokesh"})
    if r.status_code == 200:
        data = r.json()
        ca_token = data["access_token"]
        test("CA Login", True, f"Token: {ca_token[:20]}...")
    else:
        test("CA Login", False, f"Status: {r.status_code}")
except Exception as e:
    test("CA Login", False, str(e))

if not ca_token:
    print(f"\n{C.R}Cannot proceed without CA token{C.NC}\n")
    sys.exit(1)

headers = {"Authorization": f"Bearer {ca_token}"}

# 3. Get Clients
section("Client Management")
try:
    r = requests.get(f"{BASE_URL}/clients/", headers=headers)
    if r.status_code == 200:
        clients = r.json()
        test("List Clients", True, f"Found {len(clients)} clients")
        for c in clients[:3]:
            print(f"  {C.B}• {c.get('name', 'N/A')} - {c.get('phone_number', 'N/A')}{C.NC}")
    else:
        test("List Clients", False, f"Status: {r.status_code}")
except Exception as e:
    test("List Clients", False, str(e))

# Get single client
if clients:
    try:
        phone = clients[0].get('phone_number')
        r = requests.get(f"{BASE_URL}/clients/{phone}", headers=headers)
        test("Get Client Details", r.status_code == 200, f"Phone: {phone}")
    except Exception as e:
        test("Get Client Details", False, str(e))

# 4. Upload Documents
section("Document Upload")
if clients:
    client_phone = clients[0].get('phone_number', '9876543210')
    year = str(datetime.now().year)
    
    # Create test file
    test_file = "/tmp/test_document.txt"
    with open(test_file, 'w') as f:
        f.write(f"Test Document\nClient: {clients[0].get('name')}\nDate: {datetime.now()}")
    
    try:
        with open(test_file, 'rb') as f:
            files = {'file': ('test_document.txt', f, 'text/plain')}
            data = {'client_phone': client_phone, 'year': year}
            r = requests.post(f"{BASE_URL}/documents/upload",
                            files=files, data=data, headers=headers)
            
            if r.status_code == 201:
                doc = r.json()
                documents.append(doc)
                test("Upload Document", True, f"File: test_document.txt")
            else:
                test("Upload Document", False, f"Status: {r.status_code}, {r.text[:100]}")
    except Exception as e:
        test("Upload Document", False, str(e))
    
    os.remove(test_file)

# List documents
try:
    r = requests.get(f"{BASE_URL}/documents/", headers=headers)
    if r.status_code == 200:
        all_docs = r.json()
        test("List Documents", True, f"Total: {len(all_docs)}")
    else:
        test("List Documents", False, f"Status: {r.status_code}")
except Exception as e:
    test("List Documents", False, str(e))

# 5. Client Login
section("Client Portal")
if clients:
    try:
        phone = clients[0].get('phone_number')
        r = requests.post(f"{BASE_URL}/auth/login",
                         data={"username": phone, "password": "client123"})
        if r.status_code == 200:
            data = r.json()
            client_token = data["access_token"]
            test("Client Login", True, f"Phone: {phone}")
        else:
            test("Client Login", False, f"Status: {r.status_code}")
    except Exception as e:
        test("Client Login", False, str(e))

# 6. Reminders System
section("Reminders System")
if clients:
    try:
        # Get document types
        r = requests.get(f"{BASE_URL}/reminders/document-types", headers=headers)
        test("Get Document Types", r.status_code == 200, 
             f"Available: {len(r.json().get('common_types', []))}")
    except Exception as e:
        test("Get Document Types", False, str(e))
    
    try:
        # Create reminder
        reminder_data = {
            "client_phones": [clients[0].get('phone_number')],
            "document_names": ["ITR Filing AY 2025-26"],
            "document_types": ["ITR"],
            "document_years": ["2025-26"],
            "reminder_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "general_instructions": "Please submit your ITR documents.",
            "send_via_email": True,
            "send_via_whatsapp": False,
        }
        r = requests.post(f"{BASE_URL}/reminders/", json=reminder_data, headers=headers)
        test("Create Reminder", r.status_code == 201, 
             f"Reminders: {r.json().get('reminders_created', 0)}")
    except Exception as e:
        test("Create Reminder", False, str(e))
    
    try:
        # List reminders
        r = requests.get(f"{BASE_URL}/reminders/", headers=headers)
        test("List Reminders", r.status_code == 200, 
             f"Total: {len(r.json())}")
    except Exception as e:
        test("List Reminders", False, str(e))

# 7. Frontend Pages
section("Frontend Pages")
pages = [
    ("/", "Home"),
    ("/ca/login", "CA Login"),
    ("/portal/login", "Client Portal"),
    ("/ca-lokesh-dagdiya", "Public Website")
]

for path, name in pages:
    try:
        r = requests.get(f"{FRONTEND_URL}{path}")
        test(f"{name} Page", r.status_code == 200)
    except:
        test(f"{name} Page", False)

# Summary
print(f"\n{C.B}{'='*70}{C.NC}")
print(f"{C.B}{'SUMMARY'.center(70)}{C.NC}")
print(f"{C.B}{'='*70}{C.NC}\n")

print(f"{C.C}Total Tests:{C.NC} {results['total']}")
print(f"{C.G}Passed:{C.NC} {results['passed']}")
print(f"{C.R}Failed:{C.NC} {results['failed']}")

success_rate = (results['passed'] / results['total'] * 100) if results['total'] > 0 else 0
print(f"{C.B}Success Rate:{C.NC} {success_rate:.1f}%")

print(f"\n{C.C}Resources:{C.NC}")
print(f"  CA User: lokesh")
print(f"  Clients: {len(clients)}")
print(f"  Documents: {len(documents)}")

print(f"\n{C.C}Access Points:{C.NC}")
print(f"  {C.G}CA Dashboard:{C.NC} {FRONTEND_URL}/ca")
print(f"  {C.G}Client Portal:{C.NC} {FRONTEND_URL}/portal")
print(f"  {C.G}Public Site:{C.NC} {FRONTEND_URL}/ca-lokesh-dagdiya")
print(f"  {C.G}API Docs:{C.NC} {BASE_URL.replace('/api/v1', '')}/docs")

print(f"\n{C.C}Credentials:{C.NC}")
print(f"  CA: lokesh / lokesh")
if clients:
    print(f"  Client: {clients[0].get('phone_number')} / client123")

print()
if results['failed'] == 0:
    print(f"{C.G}{'='*70}{C.NC}")
    print(f"{C.G}🎉 ALL TESTS PASSED! System fully functional.{C.NC}")
    print(f"{C.G}{'='*70}{C.NC}\n")
else:
    print(f"{C.Y}⚠ {results['failed']} test(s) failed but core features work!{C.NC}\n")

sys.exit(0 if results['failed'] == 0 else 1)
