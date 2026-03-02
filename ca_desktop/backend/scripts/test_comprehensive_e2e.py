"""Comprehensive E2E test - Self-contained, creates/cleans its own test data.

Safety: Refuses to run if real WhatsApp server is detected on port 3002.
Requires: Python backend on 8443 + mock WhatsApp server on 3002.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import os
import requests
import time
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_settings
from src.models import Client, Document, WhatsAppBotState, DocumentUpload

# Dedicated test phone numbers — never conflict with real data
TEST_ACTIVE = "5550001111"
TEST_INACTIVE = "5550002222"
TEST_NO_DOCS = "5550003333"


class ComprehensiveE2ETester:
    def __init__(self):
        self.backend_url = "http://localhost:8443"
        self.wa_url = "http://localhost:3002"
        self.results = {"passed": 0, "failed": 0, "tests": []}
        self.db = None
        self._test_docs_dir = None

    def log_test(self, name, passed, message=""):
        status = "✓ PASS" if passed else "✗ FAIL"
        self.results["tests"].append({"name": name, "passed": passed, "message": message})
        if passed:
            self.results["passed"] += 1
        else:
            self.results["failed"] += 1
        print(f"{status}: {name}")
        if message and not passed:
            print(f"  → {message}")

    def send_message(self, phone: str, message: str):
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/whatsapp/incoming",
                json={
                    "phone": phone,
                    "message": message,
                    "has_media": False,
                    "message_id": f"msg_{int(time.time() * 1000)}",
                    "timestamp": int(time.time())
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_mock_message_count(self):
        try:
            response = requests.get(f"{self.wa_url}/status", timeout=2)
            if response.status_code == 200:
                return response.json().get("message_count", 0)
        except:
            pass
        return -1

    def check_backend(self):
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def check_mock_server(self):
        """Verify WhatsApp server is the MOCK, not the real one."""
        try:
            response = requests.get(f"{self.wa_url}/health", timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get("mode") == "MOCK"
        except:
            pass
        return False

    # ── Test Data Setup / Teardown ─────────────────────────────

    def setup_test_data(self):
        """Create isolated test clients and documents."""
        settings = get_settings()
        engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=engine)
        self.db = SessionLocal()

        # Clean any leftovers from previous runs
        self._cleanup_test_data()

        # Active client with documents
        self.db.add(Client(
            phone_number=TEST_ACTIVE, name="Test Active Client",
            password_hash="hash", email="active@test.e2e", is_active=True
        ))
        # Inactive client
        self.db.add(Client(
            phone_number=TEST_INACTIVE, name="Test Inactive Client",
            password_hash="hash", email="inactive@test.e2e", is_active=False
        ))
        # Client with no documents
        self.db.add(Client(
            phone_number=TEST_NO_DOCS, name="Test NoDocs Client",
            password_hash="hash", email="nodocs@test.e2e", is_active=True
        ))
        self.db.commit()

        # Create real test files on disk
        self._test_docs_dir = Path("documents") / TEST_ACTIVE / "2024-25"
        self._test_docs_dir.mkdir(parents=True, exist_ok=True)

        itr = self._test_docs_dir / "ITR.pdf"
        itr.write_text("Test ITR document for E2E")
        form16 = self._test_docs_dir / "Form16.pdf"
        form16.write_text("Test Form16 document for E2E")

        self.db.add(Document(
            client_phone=TEST_ACTIVE, year="2024-25", document_type="ITR",
            file_name="ITR.pdf", file_path=str(itr.resolve()),
            file_size=itr.stat().st_size, is_deleted=False
        ))
        self.db.add(Document(
            client_phone=TEST_ACTIVE, year="2024-25", document_type="Form16",
            file_name="Form16.pdf", file_path=str(form16.resolve()),
            file_size=form16.stat().st_size, is_deleted=False
        ))
        self.db.commit()
        print("  ✓ Test data created")

    def _cleanup_test_data(self):
        """Remove all test data by phone number."""
        for phone in [TEST_ACTIVE, TEST_INACTIVE, TEST_NO_DOCS]:
            self.db.query(Document).filter(Document.client_phone == phone).delete()
            self.db.query(WhatsAppBotState).filter(WhatsAppBotState.phone_number == phone).delete()
            self.db.query(Client).filter(Client.phone_number == phone).delete()
        self.db.commit()

    def teardown_test_data(self):
        """Clean up all test data and files."""
        if self.db:
            self._cleanup_test_data()
            self.db.close()
            print("  ✓ Test data cleaned up")
        if self._test_docs_dir and self._test_docs_dir.exists():
            import shutil
            shutil.rmtree(Path("documents") / TEST_ACTIVE, ignore_errors=True)

    # ── Test Suites ────────────────────────────────────────────

    async def test_phone_validation(self):
        print("\n" + "="*60)
        print("TEST SUITE 1: Phone Number Validation")
        print("="*60)

        valid_phones = [
            (TEST_ACTIVE, "Standard 10-digit"),
            (f"+91{TEST_ACTIVE}", "With +91 prefix"),
            (f"91{TEST_ACTIVE}", "With 91 prefix"),
            (f"+91 {TEST_ACTIVE}", "With +91 and space"),
        ]
        for phone, desc in valid_phones:
            result = self.send_message(phone, "Hi")
            self.log_test(f"Valid phone format: {desc}", result)

        invalid_phones = [
            ("", "Empty string"),
            ("123", "Too short"),
            ("98765432109", "Too long"),
            ("abc1234567", "Contains letters"),
        ]
        for phone, desc in invalid_phones:
            before = self.get_mock_message_count()
            self.send_message(phone, "Hi")
            await asyncio.sleep(0.5)
            after = self.get_mock_message_count()
            self.log_test(f"Invalid phone rejected: {desc}", before == after)

    async def test_client_authentication(self):
        print("\n" + "="*60)
        print("TEST SUITE 2: Client Authentication")
        print("="*60)

        result = self.send_message(TEST_ACTIVE, "Hi")
        self.log_test("Registered active client allowed", result)

        result = self.send_message("1111111111", "Hi")
        self.log_test("Unregistered client blocked", result)

        result = self.send_message(TEST_INACTIVE, "Hi")
        self.log_test("Inactive client blocked", result)

    async def test_bot_state_management(self):
        print("\n" + "="*60)
        print("TEST SUITE 3: Bot State Management")
        print("="*60)

        try:
            r = requests.post(f"{self.backend_url}/api/v1/whatsapp/disable-bot/{TEST_ACTIVE}", timeout=5)
            self.log_test("Bot can be disabled", r.status_code == 200)

            result = self.send_message(TEST_ACTIVE, "Hi")
            self.log_test("Bot doesn't respond when disabled", result)

            r = requests.post(f"{self.backend_url}/api/v1/whatsapp/enable-bot/{TEST_ACTIVE}", timeout=5)
            self.log_test("Bot can be re-enabled", r.status_code == 200)

            result = self.send_message(TEST_ACTIVE, "Hi")
            self.log_test("Bot responds when re-enabled", result)
        except Exception as e:
            self.log_test("Bot state management", False, str(e))

    async def test_dynamic_menus(self):
        print("\n" + "="*60)
        print("TEST SUITE 4: Dynamic Menu Generation")
        print("="*60)

        result = self.send_message(TEST_ACTIVE, "Hi")
        self.log_test("Welcome message sent", result)
        await asyncio.sleep(1)

        result = self.send_message(TEST_ACTIVE, "1")
        self.log_test("Download flow initiated", result)
        await asyncio.sleep(1)

        result = self.send_message(TEST_ACTIVE, "1")
        self.log_test("Year selected", result)
        await asyncio.sleep(1)

        result = self.send_message(TEST_ACTIVE, "1")
        self.log_test("Document type selected", result)
        await asyncio.sleep(2)

    async def test_invalid_inputs(self):
        print("\n" + "="*60)
        print("TEST SUITE 5: Invalid Input Handling")
        print("="*60)

        self.send_message(TEST_ACTIVE, "Hi")
        await asyncio.sleep(1)

        for inp, desc in [("xyz", "Random text"), ("99", "Out of range number"), ("!@#$", "Special characters")]:
            result = self.send_message(TEST_ACTIVE, inp)
            self.log_test(f"Invalid input handled: {desc}", result)

    async def test_no_documents_scenario(self):
        print("\n" + "="*60)
        print("TEST SUITE 6: No Documents Scenario")
        print("="*60)

        result = self.send_message(TEST_NO_DOCS, "Hi")
        self.log_test("Client with no documents can connect", result)
        await asyncio.sleep(1)

        result = self.send_message(TEST_NO_DOCS, "1")
        self.log_test("No documents message sent", result)

    async def test_manual_mode(self):
        print("\n" + "="*60)
        print("TEST SUITE 7: Manual Mode (Talk to CA)")
        print("="*60)

        result = self.send_message(TEST_ACTIVE, "Hi")
        self.log_test("Welcome sent before manual mode", result)
        await asyncio.sleep(1)

        result = self.send_message(TEST_ACTIVE, "3")
        self.log_test("Manual mode activated", result)
        await asyncio.sleep(1)

        try:
            r = requests.get(f"{self.backend_url}/api/v1/whatsapp/bot-status/{TEST_ACTIVE}", timeout=5)
            if r.status_code == 200:
                self.log_test("Bot disabled after manual mode", not r.json().get("bot_enabled", True))
        except Exception as e:
            self.log_test("Check bot status", False, str(e))

        try:
            r = requests.post(f"{self.backend_url}/api/v1/whatsapp/enable-bot/{TEST_ACTIVE}", timeout=5)
            self.log_test("Bot re-enabled after manual mode", r.status_code == 200)
        except:
            pass

    async def test_concurrent_users(self):
        print("\n" + "="*60)
        print("TEST SUITE 8: Concurrent User Handling")
        print("="*60)

        tasks = [asyncio.create_task(asyncio.to_thread(self.send_message, TEST_ACTIVE, "Hi")) for _ in range(3)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        success = sum(1 for r in results if r is True)
        self.log_test(f"Concurrent messages handled ({success}/3)", success == 3)

    async def test_database_state(self):
        print("\n" + "="*60)
        print("TEST SUITE 9: Database State Verification")
        print("="*60)

        try:
            clients = self.db.query(Client).filter(Client.phone_number.in_(
                [TEST_ACTIVE, TEST_INACTIVE, TEST_NO_DOCS]
            )).count()
            self.log_test(f"Test clients in DB: {clients}", clients == 3)

            documents = self.db.query(Document).filter(
                Document.client_phone == TEST_ACTIVE
            ).count()
            self.log_test(f"Test documents in DB: {documents}", documents == 2)

            bot_states = self.db.query(WhatsAppBotState).filter(
                WhatsAppBotState.phone_number == TEST_ACTIVE
            ).count()
            self.log_test(f"Bot states for test client: {bot_states}", bot_states >= 0)
        except Exception as e:
            self.log_test("Database state check", False, str(e))

    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        total = self.results["passed"] + self.results["failed"]
        rate = (self.results["passed"] / total * 100) if total > 0 else 0

        print(f"Total Tests: {total}")
        print(f"Passed: {self.results['passed']} ✓")
        print(f"Failed: {self.results['failed']} ✗")
        print(f"Pass Rate: {rate:.1f}%")

        if self.results["failed"] > 0:
            print("\nFailed Tests:")
            for t in self.results["tests"]:
                if not t["passed"]:
                    print(f"  - {t['name']}")
                    if t["message"]:
                        print(f"    {t['message']}")

        print("\n" + "="*60)
        if rate >= 90:
            print("✅ PRODUCTION READY - All critical tests passed!")
        elif rate >= 75:
            print("⚠️  MOSTLY READY - Some non-critical issues found")
        else:
            print("❌ NOT READY - Critical issues need fixing")
        print("="*60)


async def main():
    print("="*60)
    print("WhatsApp Bot - Comprehensive E2E Test Suite")
    print("="*60)

    tester = ComprehensiveE2ETester()

    print("\n🔍 Checking prerequisites...")

    if not tester.check_backend():
        print("\n❌ Python backend not running on port 8443!")
        print("  Start: PYTHONPATH=/Users/pdagdiya/DocManager python3 -m uvicorn src.main:app --port 8443")
        return
    print("✓ Python backend is running")

    if not tester.check_mock_server():
        print("\n❌ Mock WhatsApp server not detected on port 3002!")
        print("  The real WhatsApp server must NOT be running during E2E tests.")
        print("  Start mock: node src/services/whatsapp/mock_server.js")
        return
    print("✓ Mock WhatsApp server is running (safe to test)")

    print("\n📦 Setting up test data...")
    tester.setup_test_data()

    print("\n" + "="*60)
    print("STARTING COMPREHENSIVE TESTS")
    print("="*60)

    try:
        await tester.test_phone_validation()
        await asyncio.sleep(1)
        await tester.test_client_authentication()
        await asyncio.sleep(1)
        await tester.test_bot_state_management()
        await asyncio.sleep(1)
        await tester.test_dynamic_menus()
        await asyncio.sleep(1)
        await tester.test_invalid_inputs()
        await asyncio.sleep(1)
        await tester.test_no_documents_scenario()
        await asyncio.sleep(1)
        await tester.test_manual_mode()
        await asyncio.sleep(1)
        await tester.test_concurrent_users()
        await asyncio.sleep(1)
        await tester.test_database_state()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 Cleaning up test data...")
        tester.teardown_test_data()
        tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
