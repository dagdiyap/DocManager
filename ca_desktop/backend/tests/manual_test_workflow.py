"""Manual test script for WhatsApp bot workflow."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio
from datetime import datetime

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import Client, Document
from src.services.whatsapp.handler import MessageHandler


def setup_test_data(db):
    """Create test client and documents."""
    print("\n=== Setting up test data ===")
    
    client = Client(
        phone_number="9876543210",
        name="Test Client Rajesh",
        password_hash="dummy",
        email="test@example.com",
        is_active=True
    )
    db.add(client)
    
    docs_dir = Path("documents/9876543210/2024-25")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = docs_dir / "ITR.pdf"
    test_file.write_text("This is a test ITR document")
    
    doc1 = Document(
        client_phone="9876543210",
        year="2024-25",
        document_type="ITR",
        file_name="ITR.pdf",
        file_path=str(test_file),
        is_deleted=False
    )
    db.add(doc1)
    
    test_file2 = docs_dir / "Form16.pdf"
    test_file2.write_text("This is a test Form 16 document")
    
    doc2 = Document(
        client_phone="9876543210",
        year="2024-25",
        document_type="Form16",
        file_name="Form16.pdf",
        file_path=str(test_file2),
        is_deleted=False
    )
    db.add(doc2)
    
    db.commit()
    print("✓ Test client created: 9876543210 (Test Client Rajesh)")
    print("✓ Test documents created: ITR.pdf, Form16.pdf")


async def test_welcome_flow(handler, phone):
    """Test welcome message."""
    print("\n=== Test 1: Welcome Flow ===")
    print(f"Sending: Hi")
    await handler.handle_message(phone, "Hi")
    print("✓ Welcome message should be sent")


async def test_download_flow(handler, phone):
    """Test document download flow."""
    print("\n=== Test 2: Document Download Flow ===")
    
    print("Step 1: Select Download (1)")
    await handler.handle_message(phone, "1")
    print("✓ Year menu should be sent")
    
    print("\nStep 2: Select Year (1 = 2024-25)")
    await handler.handle_message(phone, "1")
    print("✓ Document type menu should be sent")
    
    print("\nStep 3: Select Document Type (1 = ITR)")
    await handler.handle_message(phone, "1")
    print("✓ ITR document should be sent")


async def test_invalid_input(handler, phone):
    """Test invalid input handling."""
    print("\n=== Test 3: Invalid Input ===")
    print("Sending: xyz")
    await handler.handle_message(phone, "xyz")
    print("✓ Invalid input message should be sent")


async def test_unregistered_number(handler):
    """Test unregistered phone number."""
    print("\n=== Test 4: Unregistered Number ===")
    print("Sending Hi from: 1111111111")
    await handler.handle_message("1111111111", "Hi")
    print("✓ Unregistered message should be sent")


async def test_bot_state(handler, phone):
    """Test bot enable/disable."""
    print("\n=== Test 5: Bot State Management ===")
    
    print("Step 1: Disable bot (option 3 - Talk to CA)")
    await handler.handle_message(phone, "3")
    print("✓ Bot should be disabled, manual mode message sent")
    
    print("\nStep 2: Try sending message (bot disabled)")
    await handler.handle_message(phone, "Hi")
    print("✓ Bot should NOT respond (CA is chatting)")
    
    print("\nStep 3: Re-enable bot")
    handler.bot_state.enable_bot(phone)
    print("✓ Bot re-enabled")
    
    print("\nStep 4: Send Hi again")
    await handler.handle_message(phone, "Hi")
    print("✓ Bot should respond with welcome message")


def check_whatsapp_server():
    """Check if WhatsApp server is running."""
    try:
        response = requests.get("http://localhost:3002/health", timeout=2)
        return response.status_code == 200
    except:
        return False


async def main():
    print("=" * 60)
    print("WhatsApp Bot - Manual Test Workflow")
    print("=" * 60)
    
    print("\n⚠️  IMPORTANT: This tests the Python backend logic only.")
    print("    For full E2E testing, you need:")
    print("    1. WhatsApp server running (npm run whatsapp)")
    print("    2. Python backend running (uvicorn)")
    print("    3. Real WhatsApp messages from your phone")
    
    whatsapp_running = check_whatsapp_server()
    if whatsapp_running:
        print("\n✓ WhatsApp server is running on port 3002")
    else:
        print("\n⚠️  WhatsApp server NOT running (tests will use mock)")
    
    engine = create_engine("sqlite:///test_whatsapp.db")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    setup_test_data(db)
    
    handler = MessageHandler(db, whatsapp_server_url="http://localhost:3002")
    test_phone = "9876543210"
    
    try:
        await test_welcome_flow(handler, test_phone)
        await asyncio.sleep(0.5)
        
        await test_download_flow(handler, test_phone)
        await asyncio.sleep(0.5)
        
        await test_invalid_input(handler, test_phone)
        await asyncio.sleep(0.5)
        
        await test_unregistered_number(handler)
        await asyncio.sleep(0.5)
        
        await test_bot_state(handler, test_phone)
        
        print("\n" + "=" * 60)
        print("✅ All manual tests completed!")
        print("=" * 60)
        
        print("\n📝 Next Steps:")
        print("1. Start WhatsApp server: cd ca_desktop/backend && npm run whatsapp")
        print("2. Scan QR code with your phone")
        print("3. Send 'Hi' from phone number 9876543210")
        print("4. Follow the bot workflow")
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        Path("test_whatsapp.db").unlink(missing_ok=True)


if __name__ == "__main__":
    asyncio.run(main())
