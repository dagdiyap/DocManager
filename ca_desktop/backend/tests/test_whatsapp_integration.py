"""Integration tests for WhatsApp bot."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import Client, Document, DocumentUpload, WhatsAppBotState
from src.services.whatsapp.bot_state import BotStateManager
from src.services.whatsapp.document_service import DocumentService


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def test_client(test_db):
    client = Client(
        phone_number="9876543210",
        name="Test Client",
        password_hash="dummy_hash",
        email="test@example.com",
        is_active=True
    )
    test_db.add(client)
    test_db.commit()
    return client


@pytest.fixture
def test_documents(test_db, test_client):
    docs_dir = Path("documents/9876543210/2024-25")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = docs_dir / "ITR.pdf"
    test_file.write_text("dummy pdf content")
    
    doc = Document(
        client_phone="9876543210",
        year="2024-25",
        document_type="ITR",
        file_name="ITR.pdf",
        file_path=str(test_file),
        is_deleted=False
    )
    test_db.add(doc)
    test_db.commit()
    
    yield [doc]
    
    if test_file.exists():
        test_file.unlink()
    if docs_dir.exists():
        docs_dir.rmdir()


class TestDocumentService:
    
    def test_get_client_by_phone(self, test_db, test_client):
        service = DocumentService(test_db)
        
        client = service.get_client_by_phone("9876543210")
        assert client is not None
        assert client.name == "Test Client"
        
        client = service.get_client_by_phone("+919876543210")
        assert client is not None
        
        client = service.get_client_by_phone("1111111111")
        assert client is None
    
    def test_get_available_years(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        years = service.get_available_years("9876543210")
        assert len(years) == 1
        assert years[0] == "2024-25"
    
    def test_get_document_types(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        doc_types = service.get_document_types("9876543210", "2024-25")
        assert len(doc_types) == 1
        assert doc_types[0] == "ITR"
    
    def test_get_document_path(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        path = service.get_document_path("9876543210", "2024-25", "ITR")
        assert path is not None
        assert "ITR.pdf" in path
        
        path = service.get_document_path("9876543210", "2024-25", "Form16")
        assert path is None
    
    def test_save_uploaded_file(self, test_db, test_client):
        service = DocumentService(test_db)
        
        file_data = b"test file content"
        file_name = "test.pdf"
        mime_type = "application/pdf"
        
        file_path = service.save_uploaded_file(
            "9876543210", file_data, file_name, mime_type
        )
        
        assert os.path.exists(file_path)
        assert "uploads" in file_path
        
        upload = test_db.query(DocumentUpload).filter(
            DocumentUpload.client_phone == "9876543210"
        ).first()
        
        assert upload is not None
        assert upload.file_name == file_name
        assert upload.mime_type == mime_type
        assert upload.processed == False
        
        Path(file_path).unlink()


class TestBotStateManager:
    
    def test_is_bot_enabled_default(self, test_db):
        manager = BotStateManager(test_db)
        
        is_enabled = manager.is_bot_enabled("9876543210")
        assert is_enabled == True
    
    def test_disable_bot(self, test_db):
        manager = BotStateManager(test_db)
        
        manager.disable_bot("9876543210")
        
        is_enabled = manager.is_bot_enabled("9876543210")
        assert is_enabled == False
        
        state = test_db.query(WhatsAppBotState).filter(
            WhatsAppBotState.phone_number == "9876543210"
        ).first()
        
        assert state is not None
        assert state.bot_enabled == False
    
    def test_enable_bot(self, test_db):
        manager = BotStateManager(test_db)
        
        manager.disable_bot("9876543210")
        manager.enable_bot("9876543210")
        
        is_enabled = manager.is_bot_enabled("9876543210")
        assert is_enabled == True
    
    def test_set_current_flow(self, test_db):
        manager = BotStateManager(test_db)
        
        manager.set_current_flow("9876543210", "download")
        
        flow = manager.get_current_flow("9876543210")
        assert flow == "download"
        
        manager.set_current_flow("9876543210", "upload")
        flow = manager.get_current_flow("9876543210")
        assert flow == "upload"
        
        manager.set_current_flow("9876543210", None)
        flow = manager.get_current_flow("9876543210")
        assert flow is None


class TestMessageTemplates:
    
    def test_welcome_message(self):
        from src.services.whatsapp.templates import welcome_message
        
        msg = welcome_message("John Doe")
        assert "Welcome John Doe" in msg
        assert "1️⃣ Download Documents" in msg
        assert "2️⃣ Upload Documents" in msg
        assert "3️⃣ Talk to CA" in msg
    
    def test_year_menu(self):
        from src.services.whatsapp.templates import year_menu
        
        years = ["2024-25", "2023-24", "2022-23"]
        msg = year_menu(years)
        assert "Select Year" in msg
        assert "1️⃣ 2024-25" in msg
        assert "2️⃣ 2023-24" in msg
        assert "3️⃣ 2022-23" in msg
    
    def test_document_type_menu(self):
        from src.services.whatsapp.templates import document_type_menu
        
        doc_types = ["ITR", "Form 16"]
        msg = document_type_menu(doc_types)
        assert "Select Document Type" in msg
        assert "1️⃣ ITR" in msg
        assert "2️⃣ Form 16" in msg
        assert "All Documents" in msg


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
