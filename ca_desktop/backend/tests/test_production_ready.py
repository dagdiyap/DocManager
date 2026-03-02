"""Production-ready comprehensive test suite for WhatsApp bot."""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio
from datetime import datetime

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.database import Base
from src.models import Client, Document, DocumentUpload, WhatsAppBotState
from src.services.whatsapp.bot_state import BotStateManager
from src.services.whatsapp.document_service import DocumentService
from src.services.whatsapp.handler import MessageHandler


@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    
    yield session
    
    session.close()


@pytest.fixture
def active_client(test_db):
    client = Client(
        phone_number="9876543210",
        name="Active Client",
        password_hash="hash",
        email="active@test.com",
        is_active=True
    )
    test_db.add(client)
    test_db.commit()
    return client


@pytest.fixture
def inactive_client(test_db):
    client = Client(
        phone_number="9876543211",
        name="Inactive Client",
        password_hash="hash",
        email="inactive@test.com",
        is_active=False
    )
    test_db.add(client)
    test_db.commit()
    return client


@pytest.fixture
def test_documents(test_db, active_client):
    docs_dir = Path("documents/9876543210/2024-25")
    docs_dir.mkdir(parents=True, exist_ok=True)
    
    itr_file = docs_dir / "ITR.pdf"
    itr_file.write_text("ITR content")
    
    form16_file = docs_dir / "Form16.pdf"
    form16_file.write_text("Form16 content")
    
    doc1 = Document(
        client_phone="9876543210",
        year="2024-25",
        document_type="ITR",
        file_name="ITR.pdf",
        file_path=str(itr_file),
        is_deleted=False
    )
    test_db.add(doc1)
    
    doc2 = Document(
        client_phone="9876543210",
        year="2024-25",
        document_type="Form16",
        file_name="Form16.pdf",
        file_path=str(form16_file),
        is_deleted=False
    )
    test_db.add(doc2)
    
    test_db.commit()
    
    yield [doc1, doc2]
    
    if itr_file.exists():
        itr_file.unlink()
    if form16_file.exists():
        form16_file.unlink()
    if docs_dir.exists():
        docs_dir.rmdir()


class TestPhoneValidation:
    
    def test_valid_phone_numbers(self, test_db):
        handler = MessageHandler(test_db)
        
        assert handler._validate_and_normalize_phone("9876543210") == "9876543210"
        assert handler._validate_and_normalize_phone("+919876543210") == "9876543210"
        assert handler._validate_and_normalize_phone("919876543210") == "9876543210"
        assert handler._validate_and_normalize_phone("+91 9876543210") == "9876543210"
        assert handler._validate_and_normalize_phone("98765-43210") == "9876543210"
    
    def test_invalid_phone_numbers(self, test_db):
        handler = MessageHandler(test_db)
        
        assert handler._validate_and_normalize_phone("") is None
        assert handler._validate_and_normalize_phone("123") is None
        assert handler._validate_and_normalize_phone("98765432109") is None
        assert handler._validate_and_normalize_phone("abc1234567") is None
        assert handler._validate_and_normalize_phone(None) is None
        assert handler._validate_and_normalize_phone(123) is None


class TestClientAuthentication:
    
    def test_registered_active_client(self, test_db, active_client):
        service = DocumentService(test_db)
        
        client = service.get_client_by_phone("9876543210")
        assert client is not None
        assert client.name == "Active Client"
        assert client.is_active == True
    
    def test_registered_inactive_client(self, test_db, inactive_client):
        service = DocumentService(test_db)
        
        client = service.get_client_by_phone("9876543211")
        assert client is None
    
    def test_unregistered_client(self, test_db):
        service = DocumentService(test_db)
        
        client = service.get_client_by_phone("1111111111")
        assert client is None
    
    def test_phone_normalization(self, test_db, active_client):
        service = DocumentService(test_db)
        
        assert service.get_client_by_phone("9876543210") is not None
        assert service.get_client_by_phone("+919876543210") is not None
        assert service.get_client_by_phone("919876543210") is not None


class TestDocumentRetrieval:
    
    def test_get_available_years(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        years = service.get_available_years("9876543210")
        assert len(years) == 1
        assert "2024-25" in years
    
    def test_get_available_years_no_documents(self, test_db, active_client):
        service = DocumentService(test_db)
        
        years = service.get_available_years("9876543210")
        assert len(years) == 0
    
    def test_get_document_types(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        doc_types = service.get_document_types("9876543210", "2024-25")
        assert len(doc_types) == 2
        assert "ITR" in doc_types
        assert "Form16" in doc_types
    
    def test_get_document_types_invalid_year(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        doc_types = service.get_document_types("9876543210", "2023-24")
        assert len(doc_types) == 0
    
    def test_get_document_path_valid(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        path = service.get_document_path("9876543210", "2024-25", "ITR")
        assert path is not None
        assert "ITR.pdf" in path
        assert os.path.exists(path)
    
    def test_get_document_path_invalid(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        path = service.get_document_path("9876543210", "2024-25", "NonExistent")
        assert path is None
    
    def test_get_document_path_missing_file(self, test_db, active_client):
        doc = Document(
            client_phone="9876543210",
            year="2024-25",
            document_type="Missing",
            file_name="missing.pdf",
            file_path="/nonexistent/path/missing.pdf",
            is_deleted=False
        )
        test_db.add(doc)
        test_db.commit()
        
        service = DocumentService(test_db)
        path = service.get_document_path("9876543210", "2024-25", "Missing")
        assert path is None
    
    def test_get_all_documents_for_year(self, test_db, test_documents):
        service = DocumentService(test_db)
        
        paths = service.get_all_documents_for_year("9876543210", "2024-25")
        assert len(paths) == 2


class TestFileUpload:
    
    def test_save_uploaded_file(self, test_db, active_client):
        service = DocumentService(test_db)
        
        file_data = b"test file content"
        file_name = "test.pdf"
        mime_type = "application/pdf"
        
        file_path = service.save_uploaded_file("9876543210", file_data, file_name, mime_type)
        
        assert os.path.exists(file_path)
        assert "uploads" in file_path
        
        upload = test_db.query(DocumentUpload).filter(
            DocumentUpload.client_phone == "9876543210"
        ).first()
        
        assert upload is not None
        assert upload.file_name == file_name
        assert upload.file_size == len(file_data)
        
        Path(file_path).unlink()
    
    def test_save_uploaded_file_empty_data(self, test_db, active_client):
        service = DocumentService(test_db)
        
        with pytest.raises(ValueError, match="Empty file data"):
            service.save_uploaded_file("9876543210", b"", "test.pdf", "application/pdf")
    
    def test_save_uploaded_file_too_large(self, test_db, active_client):
        service = DocumentService(test_db)
        
        large_data = b"x" * (101 * 1024 * 1024)
        
        with pytest.raises(ValueError, match="File too large"):
            service.save_uploaded_file("9876543210", large_data, "large.pdf", "application/pdf")
    
    def test_save_uploaded_file_invalid_filename(self, test_db, active_client):
        service = DocumentService(test_db)
        
        file_data = b"test"
        file_name = "test/../../../etc/passwd"
        
        file_path = service.save_uploaded_file("9876543210", file_data, file_name, "text/plain")
        
        assert os.path.exists(file_path)
        assert "etc" not in file_path
        assert "passwd" not in file_path
        
        Path(file_path).unlink()


class TestBotState:
    
    def test_bot_enabled_by_default(self, test_db):
        manager = BotStateManager(test_db)
        
        assert manager.is_bot_enabled("9876543210") == True
    
    def test_disable_enable_bot(self, test_db):
        manager = BotStateManager(test_db)
        
        manager.disable_bot("9876543210")
        assert manager.is_bot_enabled("9876543210") == False
        
        manager.enable_bot("9876543210")
        assert manager.is_bot_enabled("9876543210") == True
    
    def test_flow_tracking(self, test_db):
        manager = BotStateManager(test_db)
        
        manager.set_current_flow("9876543210", "download")
        assert manager.get_current_flow("9876543210") == "download"
        
        manager.set_current_flow("9876543210", "upload")
        assert manager.get_current_flow("9876543210") == "upload"
        
        manager.set_current_flow("9876543210", None)
        assert manager.get_current_flow("9876543210") is None


class TestMessageHandling:
    
    @pytest.mark.asyncio
    async def test_unregistered_user_blocked(self, test_db):
        handler = MessageHandler(test_db, whatsapp_server_url="http://mock")
        
        messages_sent = []
        
        async def mock_send(phone, text):
            messages_sent.append((phone, text))
        
        handler.send_message = mock_send
        
        await handler.handle_message("1111111111", "Hi")
        
        assert len(messages_sent) == 1
        assert "not registered" in messages_sent[0][1].lower()
    
    @pytest.mark.asyncio
    async def test_inactive_client_blocked(self, test_db, inactive_client):
        handler = MessageHandler(test_db, whatsapp_server_url="http://mock")
        
        messages_sent = []
        
        async def mock_send(phone, text):
            messages_sent.append((phone, text))
        
        handler.send_message = mock_send
        
        await handler.handle_message("9876543211", "Hi")
        
        assert len(messages_sent) == 1
        assert "inactive" in messages_sent[0][1].lower()
    
    @pytest.mark.asyncio
    async def test_bot_disabled_no_response(self, test_db, active_client):
        handler = MessageHandler(test_db, whatsapp_server_url="http://mock")
        
        handler.bot_state.disable_bot("9876543210")
        
        messages_sent = []
        
        async def mock_send(phone, text):
            messages_sent.append((phone, text))
        
        handler.send_message = mock_send
        
        await handler.handle_message("9876543210", "Hi")
        
        assert len(messages_sent) == 0
    
    @pytest.mark.asyncio
    async def test_invalid_phone_format(self, test_db):
        handler = MessageHandler(test_db, whatsapp_server_url="http://mock")
        
        messages_sent = []
        
        async def mock_send(phone, text):
            messages_sent.append((phone, text))
        
        handler.send_message = mock_send
        
        await handler.handle_message("invalid", "Hi")
        
        assert len(messages_sent) == 0
    
    @pytest.mark.asyncio
    async def test_empty_message(self, test_db, active_client):
        handler = MessageHandler(test_db, whatsapp_server_url="http://mock")
        
        messages_sent = []
        
        async def mock_send(phone, text):
            messages_sent.append((phone, text))
        
        handler.send_message = mock_send
        
        await handler.handle_message("9876543210", "")
        
        assert len(messages_sent) == 0


class TestDynamicMenus:
    
    @pytest.mark.asyncio
    async def test_year_menu_dynamic(self, test_db, active_client):
        doc1 = Document(
            client_phone="9876543210",
            year="2024-25",
            document_type="ITR",
            file_name="itr.pdf",
            file_path="/tmp/itr.pdf",
            is_deleted=False
        )
        doc2 = Document(
            client_phone="9876543210",
            year="2023-24",
            document_type="ITR",
            file_name="itr2.pdf",
            file_path="/tmp/itr2.pdf",
            is_deleted=False
        )
        test_db.add_all([doc1, doc2])
        test_db.commit()
        
        handler = MessageHandler(test_db, whatsapp_server_url="http://mock")
        
        messages_sent = []
        
        async def mock_send(phone, text):
            messages_sent.append((phone, text))
        
        handler.send_message = mock_send
        
        await handler.handle_download_start("9876543210")
        
        assert len(messages_sent) == 1
        assert "2024-25" in messages_sent[0][1]
        assert "2023-24" in messages_sent[0][1]
    
    @pytest.mark.asyncio
    async def test_no_documents_message(self, test_db, active_client):
        handler = MessageHandler(test_db, whatsapp_server_url="http://mock")
        
        messages_sent = []
        
        async def mock_send(phone, text):
            messages_sent.append((phone, text))
        
        handler.send_message = mock_send
        
        await handler.handle_download_start("9876543210")
        
        assert len(messages_sent) == 1
        assert "no documents" in messages_sent[0][1].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
