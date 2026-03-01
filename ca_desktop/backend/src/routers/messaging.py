"""Messaging and manual file sharing router."""

import shutil
from datetime import datetime
from pathlib import Path

from ca_desktop.backend.src import database, models, schemas
from ca_desktop.backend.src.dependencies import (
    get_current_ca,
    get_current_user_data,
)
from ca_desktop.backend.src.modules.files.streamer import FileStreamer
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile
from shared.crypto import create_download_token, verify_download_token
from shared.utils import sanitize_filename
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter(prefix="/messaging", tags=["Messaging"])


@router.get("/shared-files/download-token/{file_id}")
def get_shared_file_download_token(
    file_id: int,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user_data),
):
    """Generate a download token for a shared file."""
    from ca_desktop.backend.src.config import get_settings

    settings = get_settings()

    shared_file = db.query(models.SharedFile).filter(models.SharedFile.id == file_id).first()
    if not shared_file:
        raise HTTPException(status_code=404, detail="File not found")

    # Permissions check
    if current_user["user_type"] == "client":
        client = db.query(models.Client).filter(models.Client.id == current_user["user_id"]).first()
        if shared_file.client_phone != client.phone_number:
            raise HTTPException(status_code=403, detail="Access denied")

    # Generate token
    token = create_download_token(
        client_phone=shared_file.client_phone,
        file_path=shared_file.file_path,  # relative path
        secret_key=settings.secret_key,
        expiry_seconds=settings.token_expiry_seconds,
    )

    return {
        "token": token,
        "download_url": f"/api/v1/messaging/shared-files/download/{token}",
    }


@router.get("/shared-files/download/{token}")
def download_shared_file(token: str, request: Request, db: Session = Depends(database.get_db)):
    """Download a shared file using a token."""
    from ca_desktop.backend.src.config import get_settings

    settings = get_settings()

    try:
        # 1. Check if token already used
        if db.query(models.Download).filter(models.Download.download_token == token).first():
            raise HTTPException(status_code=403, detail="Token already used")

        # 2. Verify Token
        token_data = verify_download_token(token, settings.secret_key)

        # 3. Find Shared File
        shared_file = (
            db.query(models.SharedFile)
            .filter(models.SharedFile.file_path == token_data.file_path)
            .first()
        )
        if not shared_file:
            raise HTTPException(status_code=404, detail="File not found")

        # 4. Log Download
        download_log = models.Download(
            client_phone=token_data.client_phone,
            download_type="shared_file",
            file_id=shared_file.id,
            download_token=token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )
        # Update is_downloaded flag
        shared_file.is_downloaded = True
        shared_file.downloaded_at = datetime.utcnow()

        db.add(download_log)
        db.commit()

        streamer = FileStreamer()
        return streamer.get_response(token_data.file_path, is_shared=True)

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Shared file download blocked: {str(e)}")
        raise HTTPException(status_code=403, detail="Invalid or expired download token") from e


@router.post("/messages", response_model=schemas.Message)
def send_message(
    msg_in: schemas.MessageCreate,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """Send a manual message to a client."""
    # Verify client exists
    client = (
        db.query(models.Client).filter(models.Client.phone_number == msg_in.client_phone).first()
    )
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    new_msg = models.Message(
        client_phone=msg_in.client_phone,
        subject=msg_in.subject,
        body=msg_in.body,
        sent_by_user_id=current_ca.id,
    )
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


@router.get("/messages", response_model=list[schemas.Message])
def get_messages(
    db: Session = Depends(database.get_db), current_user=Depends(get_current_user_data)
):
    """Get messages for the current user."""
    query = db.query(models.Message)

    if current_user["user_type"] == "client":
        client = db.query(models.Client).filter(models.Client.id == current_user["user_id"]).first()
        query = query.filter(models.Message.client_phone == client.phone_number)

    return query.order_by(models.Message.sent_at.desc()).all()


@router.post("/shared-files", response_model=schemas.SharedFile)
async def upload_shared_file(
    client_phone: str,
    description: str = "",
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """Upload a manual file to share with a client."""
    from ca_desktop.backend.src.config import get_settings

    settings = get_settings()

    # 1. Validate client
    client = db.query(models.Client).filter(models.Client.phone_number == client_phone).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # 2. Prepare storage
    sanitized_name = sanitize_filename(file.filename)
    dest_dir = Path(settings.shared_files_root) / client_phone
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / sanitized_name

    # 3. Save file
    try:
        with dest_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        logger.error(f"Failed to save shared file: {e}")
        raise HTTPException(status_code=500, detail="File storage failed") from e

    # 4. Save to DB
    new_shared = models.SharedFile(
        client_phone=client_phone,
        file_name=sanitized_name,
        file_path=str(dest_path.relative_to(settings.shared_files_root)).replace("\\", "/"),
        file_size=dest_path.stat().st_size,
        description=description,
        sent_by_user_id=current_ca.id,
    )
    db.add(new_shared)
    db.commit()
    db.refresh(new_shared)

    return new_shared


@router.get("/shared-files", response_model=list[schemas.SharedFile])
def list_shared_files(
    db: Session = Depends(database.get_db), current_user=Depends(get_current_user_data)
):
    """List manually shared files."""
    query = db.query(models.SharedFile)

    if current_user["user_type"] == "client":
        client = db.query(models.Client).filter(models.Client.id == current_user["user_id"]).first()
        query = query.filter(models.SharedFile.client_phone == client.phone_number)

    return query.order_by(models.SharedFile.sent_at.desc()).all()
