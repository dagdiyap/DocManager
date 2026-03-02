"""WhatsApp bot API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..services.whatsapp.handler import MessageHandler

router = APIRouter(tags=["whatsapp"])


class IncomingMessage(BaseModel):
    """Incoming WhatsApp message."""
    phone: str
    message: str
    has_media: bool = False
    message_id: str
    timestamp: int


@router.post("/whatsapp/incoming")
async def handle_incoming_message(
    msg: IncomingMessage,
    db: Session = Depends(get_db)
):
    """Handle incoming WhatsApp message from Node.js server."""
    try:
        handler = MessageHandler(db)
        await handler.handle_message(msg.phone, msg.message)
        return {"status": "ok"}
    except Exception as e:
        print(f"[WhatsApp API] Error handling message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp/upload")
async def handle_media_upload(
    phone: str = Form(...),
    file: UploadFile = File(...),
    mimetype: str = Form(...),
    db: Session = Depends(get_db)
):
    """Handle media file upload from WhatsApp."""
    try:
        # Read file data
        file_data = await file.read()
        
        # Process upload
        handler = MessageHandler(db)
        await handler.handle_media_upload(
            phone=phone,
            file_data=file_data,
            file_name=file.filename or "file",
            mime_type=mimetype
        )
        
        return {"status": "ok", "filename": file.filename}
    except Exception as e:
        print(f"[WhatsApp API] Error handling upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whatsapp/enable-bot/{phone}")
async def enable_bot(phone: str, db: Session = Depends(get_db)):
    """Enable bot mode for a phone number (CA can re-enable after manual chat)."""
    from ..services.whatsapp.bot_state import BotStateManager
    
    bot_state = BotStateManager(db)
    bot_state.enable_bot(phone)
    
    return {"status": "ok", "bot_enabled": True}


@router.post("/whatsapp/disable-bot/{phone}")
async def disable_bot(phone: str, db: Session = Depends(get_db)):
    """Disable bot mode for a phone number (CA takes over manually)."""
    from ..services.whatsapp.bot_state import BotStateManager
    
    bot_state = BotStateManager(db)
    bot_state.disable_bot(phone)
    
    return {"status": "ok", "bot_enabled": False}


@router.get("/whatsapp/bot-status/{phone}")
async def get_bot_status(phone: str, db: Session = Depends(get_db)):
    """Get bot status for a phone number."""
    from ..services.whatsapp.bot_state import BotStateManager
    
    bot_state = BotStateManager(db)
    is_enabled = bot_state.is_bot_enabled(phone)
    current_flow = bot_state.get_current_flow(phone)
    
    return {
        "phone": phone,
        "bot_enabled": is_enabled,
        "current_flow": current_flow
    }


@router.get("/whatsapp/uploads")
async def list_uploads(
    processed: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """List document uploads from WhatsApp."""
    from ..models import DocumentUpload
    
    query = db.query(DocumentUpload)
    
    if processed is not None:
        query = query.filter(DocumentUpload.processed == processed)
    
    uploads = query.order_by(DocumentUpload.uploaded_at.desc()).limit(50).all()
    
    return {
        "uploads": [
            {
                "id": u.id,
                "client_phone": u.client_phone,
                "file_name": u.file_name,
                "file_size": u.file_size,
                "mime_type": u.mime_type,
                "uploaded_at": u.uploaded_at.isoformat(),
                "processed": u.processed,
                "notes": u.notes
            }
            for u in uploads
        ]
    }


@router.patch("/whatsapp/uploads/{upload_id}")
async def update_upload(
    upload_id: int,
    processed: Optional[bool] = None,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update upload status (mark as processed, add notes)."""
    from ..models import DocumentUpload
    
    upload = db.query(DocumentUpload).filter(DocumentUpload.id == upload_id).first()
    
    if not upload:
        raise HTTPException(status_code=404, detail="Upload not found")
    
    if processed is not None:
        upload.processed = processed
    
    if notes is not None:
        upload.notes = notes
    
    db.commit()
    
    return {"status": "ok", "upload_id": upload_id}
