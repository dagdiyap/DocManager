"""Document service for WhatsApp bot."""

import logging
import os
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from ...models import Client, Document

logger = logging.getLogger(__name__)


class DocumentService:
    """Handle document download and upload operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_client_by_phone(self, phone: str) -> Optional[Client]:
        """Get client by phone number (without country code)."""
        try:
            if not phone or not isinstance(phone, str):
                logger.error(f"Invalid phone parameter: {type(phone)}")
                return None
            
            clean_phone = phone.replace('+91', '').replace('+', '').strip()
            
            if clean_phone.startswith('91') and len(clean_phone) == 12:
                clean_phone = clean_phone[2:]
            
            if not clean_phone or len(clean_phone) != 10:
                logger.warning(f"Invalid phone format: {phone}")
                return None
            
            client = self.db.query(Client).filter(
                Client.phone_number == clean_phone
            ).first()
            
            if client:
                logger.debug(f"Found client: {clean_phone} (active={client.is_active})")
            else:
                logger.debug(f"Client not found: {clean_phone}")
            
            return client
        except Exception as e:
            logger.error(f"Error getting client by phone {phone}: {e}", exc_info=True)
            return None
    
    def get_available_years(self, client_phone: str) -> list[str]:
        """Get distinct years with documents for a client."""
        try:
            if not client_phone:
                logger.error("Empty client_phone in get_available_years")
                return []
            
            years = self.db.query(Document.year).filter(
                Document.client_phone == client_phone,
                Document.is_deleted == False
            ).distinct().order_by(Document.year.desc()).all()
            
            result = [year[0] for year in years if year[0]]
            logger.debug(f"Found {len(result)} years for {client_phone}")
            return result
        except Exception as e:
            logger.error(f"Error getting years for {client_phone}: {e}", exc_info=True)
            return []
    
    def get_document_types(self, client_phone: str, year: str) -> list[str]:
        """Get distinct document types for a client and year."""
        try:
            if not client_phone or not year:
                logger.error(f"Invalid parameters: phone={client_phone}, year={year}")
                return []
            
            doc_types = self.db.query(Document.document_type).filter(
                Document.client_phone == client_phone,
                Document.year == year,
                Document.is_deleted == False
            ).distinct().order_by(Document.document_type).all()
            
            result = [doc_type[0] for doc_type in doc_types if doc_type[0]]
            logger.debug(f"Found {len(result)} document types for {client_phone}/{year}")
            return result
        except Exception as e:
            logger.error(f"Error getting document types for {client_phone}/{year}: {e}", exc_info=True)
            return []
    
    def get_document_path(self, client_phone: str, year: str, doc_type: str) -> Optional[str]:
        """Get file path for a specific document."""
        try:
            if not all([client_phone, year, doc_type]):
                logger.error(f"Invalid parameters: phone={client_phone}, year={year}, type={doc_type}")
                return None
            
            document = self.db.query(Document).filter(
                Document.client_phone == client_phone,
                Document.year == year,
                Document.document_type == doc_type,
                Document.is_deleted == False
            ).first()
            
            if not document:
                logger.debug(f"Document not found in DB: {client_phone}/{year}/{doc_type}")
                return None
            
            if not document.file_path:
                logger.warning(f"Document has no file_path: {document.id}")
                return None
            
            if not os.path.exists(document.file_path):
                logger.warning(f"File does not exist: {document.file_path}")
                return None
            
            if not os.path.isfile(document.file_path):
                logger.warning(f"Path is not a file: {document.file_path}")
                return None
            
            logger.debug(f"Found document: {document.file_path}")
            return document.file_path
        except Exception as e:
            logger.error(f"Error getting document path for {client_phone}/{year}/{doc_type}: {e}", exc_info=True)
            return None
    
    def get_all_documents_for_year(self, client_phone: str, year: str) -> list[str]:
        """Get all document paths for a client and year."""
        try:
            if not client_phone or not year:
                logger.error(f"Invalid parameters: phone={client_phone}, year={year}")
                return []
            
            documents = self.db.query(Document).filter(
                Document.client_phone == client_phone,
                Document.year == year,
                Document.is_deleted == False
            ).all()
            
            valid_paths = []
            for doc in documents:
                if not doc.file_path:
                    logger.warning(f"Document {doc.id} has no file_path")
                    continue
                
                if not os.path.exists(doc.file_path):
                    logger.warning(f"File does not exist: {doc.file_path}")
                    continue
                
                if not os.path.isfile(doc.file_path):
                    logger.warning(f"Path is not a file: {doc.file_path}")
                    continue
                
                valid_paths.append(doc.file_path)
            
            logger.debug(f"Found {len(valid_paths)}/{len(documents)} valid documents for {client_phone}/{year}")
            return valid_paths
        except Exception as e:
            logger.error(f"Error getting all documents for {client_phone}/{year}: {e}", exc_info=True)
            return []
    
    def save_uploaded_file(self, client_phone: str, file_data: bytes, 
                          file_name: str, mime_type: str) -> str:
        """Save uploaded file to disk and create DB entry."""
        from datetime import datetime
        from ...models import DocumentUpload
        import re
        
        try:
            if not client_phone or not file_name:
                raise ValueError("Missing required parameters")
            
            if not isinstance(file_data, bytes):
                raise TypeError(f"file_data must be bytes, got {type(file_data)}")
            
            if len(file_data) == 0:
                raise ValueError("Empty file data")
            
            if len(file_data) > 100 * 1024 * 1024:
                raise ValueError(f"File too large: {len(file_data)} bytes")
            
            base_name = os.path.basename(file_name)
            safe_filename = re.sub(r'[^a-zA-Z0-9._-]', '_', base_name)
            if not safe_filename:
                safe_filename = f"upload_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            upload_dir = Path("documents") / client_phone / "uploads" / timestamp
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = upload_dir / safe_filename
            
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Saved file: {file_path} ({len(file_data)} bytes)")
            
            upload = DocumentUpload(
                client_phone=client_phone,
                file_name=safe_filename,
                file_path=str(file_path),
                file_size=len(file_data),
                mime_type=mime_type or "application/octet-stream",
                processed=False
            )
            self.db.add(upload)
            self.db.commit()
            
            logger.info(f"Created DB entry for upload: {upload.id}")
            
            return str(file_path)
        except Exception as e:
            logger.error(f"Error saving uploaded file from {client_phone}: {e}", exc_info=True)
            self.db.rollback()
            raise
