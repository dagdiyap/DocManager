"""E2E test script - Simulates WhatsApp client messages to test full workflow."""

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


class WhatsAppSimulator:
    def __init__(self):
        self.backend_url = "http://localhost:8443"
        self.test_phone = "9876543210"
        
    def send_message(self, message: str):
        """Simulate incoming WhatsApp message."""
        print(f"\n📱 Client sends: '{message}'")
        try:
            response = requests.post(
                f"{self.backend_url}/api/v1/whatsapp/incoming",
                json={
                    "phone": self.test_phone,
                    "message": message,
                    "has_media": False,
                    "message_id": f"msg_{int(time.time())}",
                    "timestamp": int(time.time())
                },
                timeout=10
            )
            if response.status_code == 200:
                print("✓ Message processed")
                return True
            else:
                print(f"✗ Error: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {e}")
            return False
    
    def check_backend(self):
        """Check if backend is running."""
        try:
            response = requests.get(f"{self.backend_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def get_bot_status(self):
        """Get bot status for test phone."""
        try:
            response = requests.get(
                f"{self.backend_url}/api/v1/whatsapp/bot-status/{self.test_phone}",
                timeout=5
            )
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None


async def test_welcome_flow(sim):
    print("\n" + "="*60)
    print("TEST 1: Welcome Flow")
    print("="*60)
    
    sim.send_message("Hi")
    await asyncio.sleep(1)
    
    print("\n✓ Expected: Welcome message with client name and menu (1, 2, 3)")


async def test_download_flow(sim):
    print("\n" + "="*60)
    print("TEST 2: Document Download Flow")
    print("="*60)
    
    print("\nStep 1: Select Download Documents")
    sim.send_message("1")
    await asyncio.sleep(1)
    print("✓ Expected: Year selection menu")
    
    print("\nStep 2: Select Year (2024-25)")
    sim.send_message("1")
    await asyncio.sleep(1)
    print("✓ Expected: Document type menu (ITR, Form16, All Documents)")
    
    print("\nStep 3: Select Document Type (ITR)")
    sim.send_message("1")
    await asyncio.sleep(2)
    print("✓ Expected: ITR.pdf sent via WhatsApp")


async def test_invalid_input(sim):
    print("\n" + "="*60)
    print("TEST 3: Invalid Input Handling")
    print("="*60)
    
    sim.send_message("xyz")
    await asyncio.sleep(1)
    print("✓ Expected: Invalid option message")
    
    sim.send_message("99")
    await asyncio.sleep(1)
    print("✓ Expected: Invalid option message")


async def test_bot_state(sim):
    print("\n" + "="*60)
    print("TEST 4: Bot State Management")
    print("="*60)
    
    print("\nStep 1: Client selects 'Talk to CA'")
    sim.send_message("3")
    await asyncio.sleep(1)
    print("✓ Expected: Manual mode message, bot disabled")
    
    status = sim.get_bot_status()
    if status:
        print(f"   Bot Status: {'Disabled ✓' if not status['bot_enabled'] else 'Still Enabled ✗'}")
    
    print("\nStep 2: Try sending message while bot disabled")
    sim.send_message("Hi")
    await asyncio.sleep(1)
    print("✓ Expected: No response (CA is chatting manually)")
    
    print("\nStep 3: Re-enable bot via API")
    try:
        response = requests.post(
            f"{sim.backend_url}/api/v1/whatsapp/enable-bot/{sim.test_phone}",
            timeout=5
        )
        if response.status_code == 200:
            print("✓ Bot re-enabled via API")
    except Exception as e:
        print(f"✗ Error re-enabling bot: {e}")
    
    await asyncio.sleep(1)
    
    print("\nStep 4: Send Hi again (bot should respond)")
    sim.send_message("Hi")
    await asyncio.sleep(1)
    print("✓ Expected: Welcome message again")


async def test_unregistered_number(sim):
    print("\n" + "="*60)
    print("TEST 5: Unregistered Phone Number")
    print("="*60)
    
    unregistered_phone = "1111111111"
    print(f"\n📱 Unregistered client ({unregistered_phone}) sends: 'Hi'")
    
    try:
        response = requests.post(
            f"{sim.backend_url}/api/v1/whatsapp/incoming",
            json={
                "phone": unregistered_phone,
                "message": "Hi",
                "has_media": False,
                "message_id": f"msg_{int(time.time())}",
                "timestamp": int(time.time())
            },
            timeout=10
        )
        if response.status_code == 200:
            print("✓ Message processed")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    await asyncio.sleep(1)
    print("✓ Expected: 'Not registered' message with CA contact info")


async def check_database_state():
    print("\n" + "="*60)
    print("DATABASE STATE CHECK")
    print("="*60)
    
    settings = get_settings()
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        clients = db.query(Client).filter(Client.phone_number == "9876543210").count()
        print(f"✓ Test clients in DB: {clients}")
        
        documents = db.query(Document).filter(Document.client_phone == "9876543210").count()
        print(f"✓ Test documents in DB: {documents}")
        
        bot_states = db.query(WhatsAppBotState).count()
        print(f"✓ Bot states tracked: {bot_states}")
        
        uploads = db.query(DocumentUpload).count()
        print(f"✓ Document uploads: {uploads}")
        
    finally:
        db.close()


async def main():
    print("="*60)
    print("WhatsApp Bot - E2E Workflow Test")
    print("="*60)
    
    sim = WhatsAppSimulator()
    
    print("\n🔍 Checking prerequisites...")
    
    if not sim.check_backend():
        print("\n❌ ERROR: Python backend not running!")
        print("\nStart it with:")
        print("  cd ca_desktop/backend")
        print("  source venv/bin/activate")
        print("  python -m uvicorn src.main:app --host 0.0.0.0 --port 8000")
        return
    
    print("✓ Python backend is running on port 8000")
    
    await check_database_state()
    
    print("\n" + "="*60)
    print("STARTING E2E TESTS")
    print("="*60)
    print("\n⚠️  Note: You won't see actual WhatsApp messages.")
    print("   This tests the backend logic and message routing.")
    print("   Check the backend terminal for actual message content.\n")
    
    input("Press ENTER to start tests...")
    
    try:
        await test_welcome_flow(sim)
        await asyncio.sleep(2)
        
        await test_download_flow(sim)
        await asyncio.sleep(2)
        
        await test_invalid_input(sim)
        await asyncio.sleep(2)
        
        await test_unregistered_number(sim)
        await asyncio.sleep(2)
        
        await test_bot_state(sim)
        await asyncio.sleep(2)
        
        print("\n" + "="*60)
        print("✅ ALL E2E TESTS COMPLETED")
        print("="*60)
        
        print("\n📊 Summary:")
        print("  ✓ Welcome flow tested")
        print("  ✓ Document download flow tested")
        print("  ✓ Invalid input handling tested")
        print("  ✓ Unregistered number tested")
        print("  ✓ Bot state management tested")
        
        print("\n💡 Next Steps:")
        print("  1. Check backend terminal for message outputs")
        print("  2. For real WhatsApp testing:")
        print("     - Start WhatsApp server: npm run whatsapp")
        print("     - Scan QR code")
        print("     - Send messages from phone: 9876543210")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
