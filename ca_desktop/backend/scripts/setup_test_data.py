"""Setup test data for WhatsApp bot E2E testing."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.models import Client, Document, Base
from src.config import get_settings
from datetime import datetime


def setup_test_data():
    settings = get_settings()
    engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        existing_client = db.query(Client).filter(Client.phone_number == "9876543210").first()
        if existing_client:
            print("✓ Test client already exists: 9876543210")
        else:
            client = Client(
                phone_number="9876543210",
                name="Test Client Rajesh",
                password_hash="dummy_hash_for_testing",
                email="test@example.com",
                client_type="Individual",
                is_active=True
            )
            db.add(client)
            db.commit()
            print("✓ Created test client: 9876543210 (Test Client Rajesh)")
        
        docs_dir = Path("documents/9876543210/2024-25")
        docs_dir.mkdir(parents=True, exist_ok=True)
        
        itr_file = docs_dir / "ITR.pdf"
        if not itr_file.exists():
            itr_file.write_text("This is a test ITR document for 2024-25")
            print(f"✓ Created test file: {itr_file}")
        
        form16_file = docs_dir / "Form16.pdf"
        if not form16_file.exists():
            form16_file.write_text("This is a test Form 16 document for 2024-25")
            print(f"✓ Created test file: {form16_file}")
        
        existing_doc1 = db.query(Document).filter(
            Document.client_phone == "9876543210",
            Document.year == "2024-25",
            Document.document_type == "ITR"
        ).first()
        
        if not existing_doc1:
            doc1 = Document(
                client_phone="9876543210",
                year="2024-25",
                document_type="ITR",
                file_name="ITR.pdf",
                file_path=str(itr_file),
                file_size=len(itr_file.read_text()),
                is_deleted=False,
                uploaded_at=datetime.utcnow()
            )
            db.add(doc1)
            print("✓ Created document record: ITR.pdf")
        
        existing_doc2 = db.query(Document).filter(
            Document.client_phone == "9876543210",
            Document.year == "2024-25",
            Document.document_type == "Form16"
        ).first()
        
        if not existing_doc2:
            doc2 = Document(
                client_phone="9876543210",
                year="2024-25",
                document_type="Form16",
                file_name="Form16.pdf",
                file_path=str(form16_file),
                file_size=len(form16_file.read_text()),
                is_deleted=False,
                uploaded_at=datetime.utcnow()
            )
            db.add(doc2)
            print("✓ Created document record: Form16.pdf")
        
        db.commit()
        
        print("\n=== Test Data Ready ===")
        print("Client Phone: 9876543210")
        print("Client Name: Test Client Rajesh")
        print("Documents: ITR.pdf, Form16.pdf (2024-25)")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    setup_test_data()
