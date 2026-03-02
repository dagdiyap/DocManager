"""Document service for WhatsApp bot."""

import os
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from ...models import Client, Document


class DocumentService:
    """Handle document download and upload operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_client_by_phone(self, phone: str) -> Optional[Client]:
        """Get client by phone number (without country code)."""
        # Remove country code if present
        clean_phone = phone.replace('+91', '').replace('+', '')
        
        client = self.db.query(Client).filter(
            Client.phone_number == clean_phone,
            Client.is_active == True
        ).first()
        
        return client
    
    def get_available_years(self, client_phone: str) -> list[str]:
        """Get distinct years with documents for a client."""
        years = self.db.query(Document.year).filter(
            Document.client_phone == client_phone,
            Document.is_deleted == False
        ).distinct().order_by(Document.year.desc()).all()
        
        return [year[0] for year in years]
    
    def get_document_types(self, client_phone: str, year: str) -> list[str]:
        """Get distinct document types for a client and year."""
        doc_types = self.db.query(Document.document_type).filter(
            Document.client_phone == client_phone,
            Document.year == year,
            Document.is_deleted == False
        ).distinct().order_by(Document.document_type).all()
        
        return [doc_type[0] for doc_type in doc_types]
    
    def get_document_path(self, client_phone: str, year: str, doc_type: str) -> Optional[str]:
        """Get file path for a specific document."""
        document = self.db.query(Document).filter(
            Document.client_phone == client_phone,
            Document.year == year,
            Document.document_type == doc_type,
            Document.is_deleted == False
        ).first()
        
        if document and os.path.exists(document.file_path):
            return document.file_path
        
        return None
    
    def get_all_documents_for_year(self, client_phone: str, year: str) -> list[str]:
        """Get all document paths for a client and year."""
        documents = self.db.query(Document).filter(
            Document.client_phone == client_phone,
            Document.year == year,
            Document.is_deleted == False
        ).all()
        
        return [doc.file_path for doc in documents if os.path.exists(doc.file_path)]
    
    def save_uploaded_file(self, client_phone: str, file_data: bytes, 
                          file_name: str, mime_type: str) -> str:
        """Save uploaded file to disk and create DB entry."""
        from datetime import datetime
        from ...models import DocumentUpload
        
        # Create upload directory structure
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        upload_dir = Path("documents") / client_phone / "uploads" / timestamp
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file
        file_path = upload_dir / file_name
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Create DB entry
        upload = DocumentUpload(
            client_phone=client_phone,
            file_name=file_name,
            file_path=str(file_path),
            file_size=len(file_data),
            mime_type=mime_type,
            processed=False
        )
        self.db.add(upload)
        self.db.commit()
        
        return str(file_path)
