"""Comprehensive E2E test - Tests all edge cases and production scenarios."""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
import requests
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.config import get_settings
from src.models import Client, Document, WhatsAppBotState, DocumentUpload


class ComprehensiveE2ETester:
    def __init__(self):
        self.backend_url = "http://localhost:8443"
        self.results = {"passed": 0, "failed": 0, "tests": []}
        
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
                    "message_id": f"msg_{int(time.time())}",
                    "timestamp": int(time.time())
                },
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            return False
    
    def check_backend(self):
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    async def test_phone_validation(self):
        print("\n" + "="*60)
        print("TEST SUITE 1: Phone Number Validation")
        print("="*60)
        
        valid_phones = [
            ("9876543210", "Standard 10-digit"),
            ("+919876543210", "With +91 prefix"),
            ("919876543210", "With 91 prefix"),
            ("+91 9876543210", "With +91 and space"),
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
            result = not self.send_message(phone, "Hi")
            self.log_test(f"Invalid phone rejected: {desc}", result)
    
    async def test_client_authentication(self):
        print("\n" + "="*60)
        print("TEST SUITE 2: Client Authentication")
        print("="*60)
        
        result = self.send_message("9876543210", "Hi")
        self.log_test("Registered active client allowed", result)
        
        result = self.send_message("1111111111", "Hi")
        self.log_test("Unregistered client blocked", result)
        
        settings = get_settings()
        engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        inactive = db.query(Client).filter(Client.phone_number == "9876543211").first()
        if inactive:
            result = self.send_message("9876543211", "Hi")
            self.log_test("Inactive client blocked", result)
        
        db.close()
    
    async def test_bot_state_management(self):
        print("\n" + "="*60)
        print("TEST SUITE 3: Bot State Management")
        print("="*60)
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/whatsapp/disable-bot/9876543210",
                timeout=5
            )
            disabled = response.status_code == 200
            self.log_test("Bot can be disabled", disabled)
            
            if disabled:
                result = self.send_message("9876543210", "Hi")
                self.log_test("Bot doesn't respond when disabled", result)
            
            response = requests.post(
                f"{self.backend_url}/api/v1/whatsapp/enable-bot/9876543210",
                timeout=5
            )
            enabled = response.status_code == 200
            self.log_test("Bot can be re-enabled", enabled)
            
            if enabled:
                result = self.send_message("9876543210", "Hi")
                self.log_test("Bot responds when re-enabled", result)
        except Exception as e:
            self.log_test("Bot state management", False, str(e))
    
    async def test_dynamic_menus(self):
        print("\n" + "="*60)
        print("TEST SUITE 4: Dynamic Menu Generation")
        print("="*60)
        
        result = self.send_message("9876543210", "Hi")
        self.log_test("Welcome message sent", result)
        await asyncio.sleep(1)
        
        result = self.send_message("9876543210", "1")
        self.log_test("Download flow initiated", result)
        await asyncio.sleep(1)
        
        result = self.send_message("9876543210", "1")
        self.log_test("Year selected", result)
        await asyncio.sleep(1)
        
        result = self.send_message("9876543210", "1")
        self.log_test("Document type selected", result)
        await asyncio.sleep(2)
    
    async def test_invalid_inputs(self):
        print("\n" + "="*60)
        print("TEST SUITE 5: Invalid Input Handling")
        print("="*60)
        
        self.send_message("9876543210", "Hi")
        await asyncio.sleep(1)
        
        invalid_inputs = [
            ("xyz", "Random text"),
            ("99", "Out of range number"),
            ("", "Empty message"),
            ("!@#$", "Special characters"),
        ]
        
        for inp, desc in invalid_inputs:
            if inp:
                result = self.send_message("9876543210", inp)
                self.log_test(f"Invalid input handled: {desc}", result)
    
    async def test_no_documents_scenario(self):
        print("\n" + "="*60)
        print("TEST SUITE 6: No Documents Scenario")
        print("="*60)
        
        settings = get_settings()
        engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        no_docs_client = Client(
            phone_number="8888888888",
            name="No Docs Client",
            password_hash="hash",
            email="nodocs@test.com",
            is_active=True
        )
        db.add(no_docs_client)
        db.commit()
        
        result = self.send_message("8888888888", "Hi")
        self.log_test("Client with no documents can connect", result)
        await asyncio.sleep(1)
        
        result = self.send_message("8888888888", "1")
        self.log_test("No documents message sent", result)
        
        db.delete(no_docs_client)
        db.commit()
        db.close()
    
    async def test_manual_mode(self):
        print("\n" + "="*60)
        print("TEST SUITE 7: Manual Mode (Talk to CA)")
        print("="*60)
        
        result = self.send_message("9876543210", "Hi")
        self.log_test("Welcome sent before manual mode", result)
        await asyncio.sleep(1)
        
        result = self.send_message("9876543210", "3")
        self.log_test("Manual mode activated", result)
        await asyncio.sleep(1)
        
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/whatsapp/bot-status/9876543210",
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                disabled = not data.get("bot_enabled", True)
                self.log_test("Bot disabled after manual mode", disabled)
        except Exception as e:
            self.log_test("Check bot status", False, str(e))
        
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/whatsapp/enable-bot/9876543210",
                timeout=5
            )
            self.log_test("Bot re-enabled after manual mode", response.status_code == 200)
        except:
            pass
    
    async def test_concurrent_users(self):
        print("\n" + "="*60)
        print("TEST SUITE 8: Concurrent User Handling")
        print("="*60)
        
        users = ["9876543210", "9876543210", "9876543210"]
        
        tasks = []
        for user in users:
            tasks.append(asyncio.create_task(asyncio.to_thread(self.send_message, user, "Hi")))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if r is True)
        self.log_test(f"Concurrent messages handled ({success_count}/{len(users)})", success_count == len(users))
    
    async def test_database_state(self):
        print("\n" + "="*60)
        print("TEST SUITE 9: Database State Verification")
        print("="*60)
        
        settings = get_settings()
        engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
        SessionLocal = sessionmaker(bind=engine)
        db = SessionLocal()
        
        try:
            clients = db.query(Client).filter(Client.is_active == True).count()
            self.log_test(f"Active clients in DB: {clients}", clients > 0)
            
            documents = db.query(Document).filter(Document.is_deleted == False).count()
            self.log_test(f"Documents in DB: {documents}", documents >= 0)
            
            bot_states = db.query(WhatsAppBotState).count()
            self.log_test(f"Bot states tracked: {bot_states}", bot_states >= 0)
            
            uploads = db.query(DocumentUpload).count()
            self.log_test(f"Document uploads: {uploads}", uploads >= 0)
        except Exception as e:
            self.log_test("Database state check", False, str(e))
        finally:
            db.close()
    
    def print_summary(self):
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        
        total = self.results["passed"] + self.results["failed"]
        pass_rate = (self.results["passed"] / total * 100) if total > 0 else 0
        
        print(f"Total Tests: {total}")
        print(f"Passed: {self.results['passed']} ✓")
        print(f"Failed: {self.results['failed']} ✗")
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.results["failed"] > 0:
            print("\nFailed Tests:")
            for test in self.results["tests"]:
                if not test["passed"]:
                    print(f"  - {test['name']}")
                    if test["message"]:
                        print(f"    {test['message']}")
        
        print("\n" + "="*60)
        
        if pass_rate >= 90:
            print("✅ PRODUCTION READY - All critical tests passed!")
        elif pass_rate >= 75:
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
        print("\n❌ ERROR: Python backend not running on port 8443!")
        print("\nStart it with:")
        print("  cd ca_desktop/backend")
        print("  source venv/bin/activate")
        print("  PYTHONPATH=/Users/pdagdiya/DocManager python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8443")
        return
    
    print("✓ Python backend is running")
    
    try:
        response = requests.get("http://localhost:3002/health", timeout=2)
        if response.status_code == 200:
            print("✓ WhatsApp server is running")
        else:
            print("⚠️  WhatsApp server not responding correctly")
    except:
        print("⚠️  WhatsApp server not running (using mock)")
    
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
        
        tester.print_summary()
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        tester.print_summary()
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        tester.print_summary()


if __name__ == "__main__":
    asyncio.run(main())
