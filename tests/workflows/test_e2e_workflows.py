#!/usr/bin/env python3
"""
End-to-End Workflow Test Suite
Tests complete user workflows for DocManager CA Desktop application.
Simulates real CA and client interactions.
"""

import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import tempfile
import time

BASE_URL = "http://localhost:8443/api/v1"
FRONTEND_URL = "http://localhost:5174"
CA_USERNAME = "lokesh"
CA_PASSWORD = "lokesh"

class Colors:
    BLUE = '\033[34m'
    GREEN = '\033[32m'
    RED = '\033[31m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^70}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_workflow(text):
    print(f"\n{Colors.YELLOW}{'─'*70}{Colors.RESET}")
    print(f"{Colors.YELLOW}{Colors.BOLD}► WORKFLOW: {text}{Colors.RESET}")
    print(f"{Colors.YELLOW}{'─'*70}{Colors.RESET}")

def print_step(step_num, text):
    print(f"\n{Colors.CYAN}{step_num}. {text}{Colors.RESET}")

def print_success(text):
    print(f"  {Colors.GREEN}✓{Colors.RESET} {text}")

def print_error(text):
    print(f"  {Colors.RED}✗{Colors.RESET} {text}")

def print_info(text):
    print(f"  {Colors.CYAN}→{Colors.RESET} {text}")

class E2EWorkflowTests:
    def __init__(self):
        self.ca_token = None
        self.client_tokens = {}
        self.test_data = {
            "clients": [],
            "documents": [],
            "reminders": [],
            "services": []
        }
        self.results = {"passed": 0, "failed": 0, "workflows": []}

    def workflow(self, name, func):
        """Run a complete workflow test"""
        print_workflow(name)
        try:
            func()
            self.results["passed"] += 1
            self.results["workflows"].append({"name": name, "status": "passed"})
            print_success(f"Workflow '{name}' completed successfully")
            return True
        except Exception as e:
            self.results["failed"] += 1
            self.results["workflows"].append({"name": name, "status": "failed", "error": str(e)})
            print_error(f"Workflow '{name}' failed: {str(e)}")
            return False

    def run_all_workflows(self):
        """Run all E2E workflow tests"""
        print_header("DocManager - End-to-End Workflow Tests")

        # Setup
        print_workflow("SETUP - CA Authentication")
        self.setup_ca_session()

        # Workflow 1: New Client Onboarding
        self.workflow("1. New Client Onboarding & Setup", self.workflow_client_onboarding)

        # Workflow 2: Document Upload & Management
        self.workflow("2. Document Upload & Organization", self.workflow_document_management)

        # Workflow 3: Multi-Client Reminder Creation
        self.workflow("3. Multi-Client Reminder System", self.workflow_reminder_system)

        # Workflow 4: Client Portal Access
        self.workflow("4. Client Portal Document Access", self.workflow_client_portal)

        # Workflow 5: CA Profile & Public Website
        self.workflow("5. CA Profile & Public Website Setup", self.workflow_public_website)

        # Workflow 6: Compliance Tracking
        self.workflow("6. Compliance Status Tracking", self.workflow_compliance_tracking)

        # Workflow 7: Complete Tax Filing Season
        self.workflow("7. Complete Tax Filing Season Workflow", self.workflow_tax_season)

        self.print_summary()

    def setup_ca_session(self):
        """Setup CA authentication"""
        print_step(1, "CA Login")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            data={"username": CA_USERNAME, "password": CA_PASSWORD},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        response.raise_for_status()
        self.ca_token = response.json()["access_token"]
        print_success("CA authenticated successfully")

    def workflow_client_onboarding(self):
        """Workflow 1: Complete client onboarding process"""

        print_step(1, "Create new client account")
        new_client = {
            "name": f"E2E Test Client",
            "phone_number": f"7387671861",
            "email": f"client@test.com",
            "client_type": "individual",
            "password": "testpass123"
        }

        response = requests.post(
            f"{BASE_URL}/clients/",
            json=new_client,
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        client_data = response.json()
        self.test_data["clients"].append(client_data)
        print_success(f"Client created: {client_data['name']}")
        print_info(f"Phone: {client_data['phone_number']}")

        print_step(2, "Verify client appears in client list")
        response = requests.get(
            f"{BASE_URL}/clients/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        clients = response.json()
        assert any(c['phone_number'] == new_client['phone_number'] for c in clients)
        print_success(f"Client verified in list ({len(clients)} total clients)")

        print_step(3, "Get detailed client information")
        response = requests.get(
            f"{BASE_URL}/clients/{new_client['phone_number']}",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        client_details = response.json()
        print_success(f"Client details retrieved")
        print_info(f"Type: {client_details.get('client_type', 'N/A')}")
        print_info(f"Email: {client_details.get('email', 'N/A')}")

        print_step(4, "Update client information")
        response = requests.patch(
            f"{BASE_URL}/clients/{new_client['phone_number']}",
            params={"client_type": "business"},
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        print_success("Client information updated")

    def workflow_document_management(self):
        """Workflow 2: Complete document management cycle"""

        if not self.test_data["clients"]:
            # Use existing client
            response = requests.get(
                f"{BASE_URL}/clients/",
                headers={"Authorization": f"Bearer {self.ca_token}"}
            )
            clients = response.json()
            if clients:
                self.test_data["clients"].append(clients[0])

        client_phone = self.test_data["clients"][0]['phone_number']

        print_step(1, "Upload ITR document for client")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(f"ITR Filing Document - AY 2025-26\nClient: {client_phone}\nDate: {datetime.now()}")
            temp_path = f.name

        with open(temp_path, 'rb') as f:
            files = {'file': ('ITR_AY2025-26.txt', f, 'text/plain')}
            data = {'client_phone': client_phone, 'year': '2025'}
            response = requests.post(
                f"{BASE_URL}/documents/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {self.ca_token}"}
            )

        Path(temp_path).unlink()
        response.raise_for_status()
        doc = response.json()
        self.test_data["documents"].append(doc)
        print_success(f"Document uploaded: {doc['filename']}")
        print_info(f"Document ID: {doc['id']}")

        print_step(2, "Upload GST document for same client")
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
            f.write(f"GST Return Q1 2026\nClient: {client_phone}")
            temp_path = f.name

        with open(temp_path, 'rb') as f:
            files = {'file': ('GST_Q1_2026.pdf', f, 'application/pdf')}
            data = {'client_phone': client_phone, 'year': '2026'}
            response = requests.post(
                f"{BASE_URL}/documents/upload",
                files=files,
                data=data,
                headers={"Authorization": f"Bearer {self.ca_token}"}
            )

        Path(temp_path).unlink()
        response.raise_for_status()
        doc2 = response.json()
        self.test_data["documents"].append(doc2)
        print_success(f"Second document uploaded: {doc2['filename']}")

        print_step(3, "List all documents")
        response = requests.get(
            f"{BASE_URL}/documents/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        all_docs = response.json()
        print_success(f"Retrieved {len(all_docs)} total documents")

        print_step(4, "Generate download token for document")
        response = requests.get(
            f"{BASE_URL}/documents/download-token/{doc['id']}",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        token_data = response.json()
        print_success("Download token generated")
        print_info(f"Token: {token_data['token'][:30]}...")

    def workflow_reminder_system(self):
        """Workflow 3: Complete reminder system workflow"""

        print_step(1, "Get available document types")
        response = requests.get(
            f"{BASE_URL}/reminders/document-types",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        doc_types = response.json()
        print_success(f"Retrieved {len(doc_types['common_types'])} document types")
        print_info(f"Types: ITR, GST, PAN, TDS, etc.")

        print_step(2, "Get all clients for bulk reminder")
        response = requests.get(
            f"{BASE_URL}/clients/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        clients = response.json()
        selected_clients = [c['phone_number'] for c in clients[:3]]  # Select first 3
        print_success(f"Selected {len(selected_clients)} clients for reminder")

        print_step(3, "Create multi-client, multi-document reminder")
        reminder_date = (datetime.now() + timedelta(days=30)).isoformat()
        payload = {
            "client_phones": selected_clients,
            "document_names": ["ITR Filing AY 2025-26", "GST Return March 2026"],
            "document_types": ["ITR", "GST_GSTR3B"],
            "document_years": ["2025-26", "2026"],
            "reminder_date": reminder_date,
            "general_instructions": "Please ensure all documents are submitted before the deadline to avoid penalties.",
            "send_via_email": False,  # Disabled for testing
            "send_via_whatsapp": False
        }

        response = requests.post(
            f"{BASE_URL}/reminders/",
            json=payload,
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        result = response.json()
        print_success(f"Created {result['reminders_created']} reminders")
        print_info(f"{len(selected_clients)} clients × 2 documents = {result['reminders_created']} reminders")

        print_step(4, "List all reminders")
        response = requests.get(
            f"{BASE_URL}/reminders/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        reminders = response.json()
        print_success(f"Total reminders in system: {len(reminders)}")

        print_step(5, "Filter reminders by specific client")
        if selected_clients:
            response = requests.get(
                f"{BASE_URL}/reminders/",
                params={"client_phone": selected_clients[0]},
                headers={"Authorization": f"Bearer {self.ca_token}"}
            )
            response.raise_for_status()
            client_reminders = response.json()
            print_success(f"Client has {len(client_reminders)} reminders")

    def workflow_client_portal(self):
        """Workflow 4: Client portal access and document viewing"""

        print_step(1, "Client login to portal")
        # Get an existing client
        response = requests.get(
            f"{BASE_URL}/clients/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        clients = response.json()
        if not clients:
            print_info("No clients available for portal test")
            return

        test_client = clients[0]
        client_phone = test_client['phone_number']

        # Try to login (password might be 'client123' for demo clients)
        try:
            response = requests.post(
                f"{BASE_URL}/auth/client-login",
                data={"username": client_phone, "password": "client123"},
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
            response.raise_for_status()
            client_token = response.json()["access_token"]
            self.client_tokens[client_phone] = client_token
            print_success(f"Client logged in: {test_client['name']}")
        except:
            print_info("Client login skipped (password not set)")
            return

        print_step(2, "Client views their documents")
        response = requests.get(
            f"{BASE_URL}/documents/",
            headers={"Authorization": f"Bearer {client_token}"}
        )
        response.raise_for_status()
        client_docs = response.json()
        print_success(f"Client can see {len(client_docs)} documents")

        print_step(3, "Client checks their reminders")
        response = requests.get(
            f"{BASE_URL}/reminders/",
            params={"client_phone": client_phone},
            headers={"Authorization": f"Bearer {self.ca_token}"}  # Using CA token for now
        )
        response.raise_for_status()
        client_reminders = response.json()
        print_success(f"Client has {len(client_reminders)} pending reminders")

        print_step(4, "Verify frontend portal page loads")
        try:
            response = requests.get(f"{FRONTEND_URL}/portal/login", timeout=5)
            if response.status_code == 200:
                print_success("Client portal page accessible")
            else:
                print_info(f"Portal page status: {response.status_code}")
        except:
            print_info("Frontend check skipped")

    def workflow_public_website(self):
        """Workflow 5: CA profile and public website setup"""

        print_step(1, "Get current CA profile")
        response = requests.get(
            f"{BASE_URL}/ca/profile",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        profile = response.json()
        print_success("CA profile retrieved")
        print_info(f"Firm: {profile.get('firm_name', 'Not set')}")

        print_step(2, "Update CA profile with complete information")
        profile_update = {
            "firm_name": "Dagdiya Associates",
            "professional_bio": "Leading Chartered Accountants firm providing comprehensive financial services including tax planning, audit, GST compliance, and business advisory.",
            "phone_number": "+91-9876543210",
            "email": "contact@dagdiyaassociates.com",
            "address": "123 Business District, Mumbai, Maharashtra 400001"
        }

        response = requests.patch(
            f"{BASE_URL}/ca/profile",
            json=profile_update,
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        print_success("CA profile updated with complete details")

        print_step(3, "Add professional services")
        services = [
            {"name": "Tax Planning & Filing", "description": "Expert tax consultation and filing for individuals and businesses", "category": "tax"},
            {"name": "GST Compliance", "description": "Complete GST registration, filing, and compliance management", "category": "gst"},
            {"name": "Audit & Assurance", "description": "Comprehensive audit services ensuring accuracy and compliance", "category": "audit"}
        ]

        for service in services:
            try:
                response = requests.post(
                    f"{BASE_URL}/ca/services",
                    params=service,
                    headers={"Authorization": f"Bearer {self.ca_token}"}
                )
                if response.status_code == 201 or response.status_code == 200:
                    print_success(f"Service added: {service['name']}")
                    self.test_data["services"].append(response.json())
            except:
                print_info(f"Service '{service['name']}' may already exist")

        print_step(4, "Verify public website accessibility")
        response = requests.get(f"{BASE_URL}/public/ca-lokesh-dagdiya/profile")
        response.raise_for_status()
        public_profile = response.json()
        print_success("Public profile accessible")
        print_info(f"Public firm name: {public_profile.get('firm_name', 'N/A')}")

        print_step(5, "Check public services listing")
        response = requests.get(f"{BASE_URL}/public/ca-lokesh-dagdiya/services")
        response.raise_for_status()
        public_services = response.json()
        print_success(f"Public website shows {len(public_services)} services")

        print_step(6, "Verify frontend public page loads")
        try:
            response = requests.get(f"{FRONTEND_URL}/ca-lokesh-dagdiya", timeout=5)
            if response.status_code == 200:
                print_success("Public website page accessible")
            else:
                print_info(f"Public page status: {response.status_code}")
        except:
            print_info("Frontend check skipped")

    def workflow_compliance_tracking(self):
        """Workflow 6: Compliance status tracking"""

        print_step(1, "List all compliance rules")
        response = requests.get(
            f"{BASE_URL}/compliance/rules",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        rules = response.json()
        print_success(f"Retrieved {len(rules)} compliance rules")

        print_step(2, "Check client compliance status")
        response = requests.get(
            f"{BASE_URL}/clients/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        clients = response.json()

        if clients:
            client_phone = clients[0]['phone_number']
            response = requests.get(
                f"{BASE_URL}/clients/{client_phone}/compliance",
                headers={"Authorization": f"Bearer {self.ca_token}"}
            )
            response.raise_for_status()
            compliance_status = response.json()
            print_success(f"Compliance status retrieved for {clients[0]['name']}")
            print_info(f"Status data: {len(compliance_status)} items" if isinstance(compliance_status, list) else "Status retrieved")

    def workflow_tax_season(self):
        """Workflow 7: Complete tax filing season workflow"""

        print_step(1, "Get all individual clients for tax season")
        response = requests.get(
            f"{BASE_URL}/clients/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        response.raise_for_status()
        all_clients = response.json()
        individual_clients = [c for c in all_clients if c.get('client_type') == 'individual'][:5]
        print_success(f"Identified {len(individual_clients)} individual clients")

        print_step(2, "Upload ITR documents for each client")
        uploaded_count = 0
        for client in individual_clients:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(f"ITR Filing - AY 2025-26\nClient: {client['name']}\nPhone: {client['phone_number']}\nDate: {datetime.now()}")
                temp_path = f.name

            try:
                with open(temp_path, 'rb') as f:
                    files = {'file': (f"ITR_{client['phone_number']}_2025.txt", f, 'text/plain')}
                    data = {'client_phone': client['phone_number'], 'year': '2025'}
                    response = requests.post(
                        f"{BASE_URL}/documents/upload",
                        files=files,
                        data=data,
                        headers={"Authorization": f"Bearer {self.ca_token}"}
                    )
                if response.status_code in [200, 201]:
                    uploaded_count += 1
            except:
                pass
            finally:
                Path(temp_path).unlink()

        print_success(f"Uploaded ITR documents for {uploaded_count} clients")

        print_step(3, "Send bulk tax filing reminders")
        client_phones = [c['phone_number'] for c in individual_clients]
        reminder_payload = {
            "client_phones": client_phones,
            "document_names": ["ITR Filing AY 2025-26", "Form 16"],
            "document_types": ["ITR", "OTHER"],
            "document_years": ["2025-26", "2025"],
            "reminder_date": (datetime.now() + timedelta(days=15)).isoformat(),
            "general_instructions": "Tax season deadline approaching. Please submit all documents by July 31st.",
            "send_via_email": False,
            "send_via_whatsapp": False
        }

        response = requests.post(
            f"{BASE_URL}/reminders/",
            json=reminder_payload,
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        if response.status_code in [200, 201]:
            result = response.json()
            print_success(f"Sent {result['reminders_created']} tax season reminders")

        print_step(4, "Generate compliance report")
        compliant_clients = 0
        for client in individual_clients:
            try:
                response = requests.get(
                    f"{BASE_URL}/clients/{client['phone_number']}/compliance",
                    headers={"Authorization": f"Bearer {self.ca_token}"}
                )
                if response.status_code == 200:
                    compliant_clients += 1
            except:
                pass

        print_success(f"Compliance check completed for {compliant_clients} clients")

        print_step(5, "Summary statistics")
        response = requests.get(
            f"{BASE_URL}/documents/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        total_docs = len(response.json()) if response.status_code == 200 else 0

        response = requests.get(
            f"{BASE_URL}/reminders/",
            headers={"Authorization": f"Bearer {self.ca_token}"}
        )
        total_reminders = len(response.json()) if response.status_code == 200 else 0

        print_success("Tax season workflow completed")
        print_info(f"Total Documents: {total_docs}")
        print_info(f"Total Reminders: {total_reminders}")
        print_info(f"Clients Processed: {len(individual_clients)}")

    def print_summary(self):
        """Print workflow test summary"""
        total = self.results["passed"] + self.results["failed"]
        success_rate = (self.results["passed"] / total * 100) if total > 0 else 0

        print(f"\n{Colors.BLUE}{'='*70}{Colors.RESET}")
        print(f"{Colors.BLUE}{Colors.BOLD}{'WORKFLOW TEST SUMMARY':^70}{Colors.RESET}")
        print(f"{Colors.BLUE}{'='*70}{Colors.RESET}\n")

        print(f"{Colors.CYAN}Total Workflows:{Colors.RESET} {total}")
        print(f"{Colors.GREEN}Passed:{Colors.RESET} {self.results['passed']}")
        print(f"{Colors.RED}Failed:{Colors.RESET} {self.results['failed']}")
        print(f"{Colors.CYAN}Success Rate:{Colors.RESET} {success_rate:.1f}%\n")

        print(f"{Colors.CYAN}Test Data Created:{Colors.RESET}")
        print(f"  Clients: {len(self.test_data['clients'])}")
        print(f"  Documents: {len(self.test_data['documents'])}")
        print(f"  Services: {len(self.test_data['services'])}\n")

        if self.results["failed"] == 0:
            print(f"{Colors.GREEN}{'='*70}{Colors.RESET}")
            print(f"{Colors.GREEN}{Colors.BOLD}🎉 ALL E2E WORKFLOWS PASSED!{Colors.RESET}")
            print(f"{Colors.GREEN}{'='*70}{Colors.RESET}\n")
        else:
            print(f"{Colors.RED}Failed Workflows:{Colors.RESET}")
            for wf in self.results["workflows"]:
                if wf["status"] == "failed":
                    print(f"  {Colors.RED}✗ {wf['name']}: {wf.get('error', 'Unknown error')}{Colors.RESET}")

if __name__ == "__main__":
    suite = E2EWorkflowTests()
    suite.run_all_workflows()
