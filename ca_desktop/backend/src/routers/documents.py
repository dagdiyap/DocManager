"""Document management and download router."""

import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from ca_desktop.backend.src import config, database, models, schemas
from ca_desktop.backend.src.dependencies import (
    get_current_ca,
    get_current_user_data,
)
from ca_desktop.backend.src.modules.documents.scanner import DocumentIndexer
from ca_desktop.backend.src.modules.files.streamer import FileStreamer
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from shared.crypto import create_download_token
from shared.utils import (
    sanitize_filename,
    validate_document_type,
    validate_phone_number,
    validate_year,
)
from shared.utils.constants import ALLOWED_FILE_EXTENSIONS
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter(prefix="/documents", tags=["Documents"])


@router.post("/upload", status_code=status.HTTP_201_CREATED, response_model=schemas.Document)
def upload_document(
    file: UploadFile = File(...),
    client_phone: str = Form(...),
    year: str = Form(...),
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user_data),
):
    """Upload a document for a client."""
    # 1. Permissions Check
    if current_user["user_type"] != "ca":
        raise HTTPException(status_code=403, detail="Only CA can upload documents")

    # 2. Validate Inputs
    try:
        phone = validate_phone_number(client_phone)
        year = validate_year(year)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    # 3. Validate File
    filename = sanitize_filename(file.filename)
    file_ext = Path(filename).suffix.lower()

    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File extension {file_ext} not allowed")

    # 4. Prepare Storage Path
    settings = config.get_settings()
    doc_root = Path(settings.documents_root)
    save_dir = doc_root / phone / year
    save_dir.mkdir(parents=True, exist_ok=True)

    save_path = save_dir / filename

    # 5. Save File & Calculate Hash
    try:
        hasher = hashlib.sha256()
        file_size = 0

        with open(save_path, "wb") as buffer:
            while True:
                chunk = file.file.read(8192)
                if not chunk:
                    break
                file_size += len(chunk)
                hasher.update(chunk)
                buffer.write(chunk)

        file_hash = hasher.hexdigest()

    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to save file") from e
    finally:
        file.file.close()

    # 6. Index in Database
    # Determine document type from filename (stem)
    doc_type_raw = Path(filename).stem
    # Attempt to validate doc type, fallback to sanitized stem if strict validation fails
    # But strict validation is required by schema/logic usually.
    # Let's try to normalize it.
    try:
        doc_type = validate_document_type(doc_type_raw)
    except Exception:
        # If filename doesn't match doc type rules strictly, maybe use a default or just the sanitized name?
        # For now, let's allow it but maybe we should enforce it?
        # The scanner enforces it. Let's enforce it here too for consistency.
        # But wait, validate_document_type allows alphanumeric+underscore.
        # Filenames can be anything. We should probably extract a type OR default to "OTHER".
        doc_type = "OTHER"

    # Check if doc exists to update or create
    existing_doc = (
        db.query(models.Document)
        .filter(
            models.Document.client_phone == phone,
            models.Document.year == year,
            models.Document.file_name == filename,
        )
        .first()
    )

    if existing_doc:
        existing_doc.file_size = file_size
        existing_doc.file_hash = file_hash
        existing_doc.modified_at = datetime.now(timezone.utc)
        existing_doc.is_deleted = False
        db.commit()
        db.refresh(existing_doc)
        return existing_doc
    else:
        new_doc = models.Document(
            client_phone=phone,
            year=year,
            document_type=doc_type,
            file_name=filename,
            file_path=str(save_path.relative_to(doc_root)).replace("\\", "/"),
            file_size=file_size,
            file_hash=file_hash,
            uploaded_at=datetime.now(timezone.utc),
            is_deleted=False,
        )
        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        return new_doc


@router.get("/scan", status_code=status.HTTP_202_ACCEPTED)
def trigger_scan(
    background_tasks: BackgroundTasks,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """Trigger a full document folder scan in the background."""
    indexer = DocumentIndexer(db)
    background_tasks.add_task(indexer.scan_all)
    return {"detail": "Scan initiated in background"}


@router.get("/search")
def search_documents(
    client_phone: Optional[str] = None,
    year: Optional[str] = None,
    tags: Optional[list[str]] = Query(None),
    file_type: Optional[str] = None,
    uploaded_after: Optional[datetime] = None,
    uploaded_before: Optional[datetime] = None,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user_data),
):
    """Search documents with filters by year, tag, file type, upload date."""
    query = db.query(models.Document).filter(models.Document.is_deleted.is_(False))

    # Permission check
    if current_user.get("user_type") == "client":
        client = (
            db.query(models.Client).filter(models.Client.id == current_user.get("user_id")).first()
        )
        query = query.filter(models.Document.client_phone == client.phone_number)
    elif client_phone:
        # CA can filter by client
        query = query.filter(models.Document.client_phone == client_phone)

    # Year filter
    if year:
        query = query.filter(models.Document.year == year)

    # Tag filter
    if tags:
        tag_objects = db.query(models.DocumentTag).filter(models.DocumentTag.name.in_(tags)).all()
        if tag_objects:
            for tag in tag_objects:
                query = query.filter(models.Document.tags.any(id=tag.id))

    # File type filter
    if file_type:
        query = query.filter(models.Document.file_name.ilike(f"%.{file_type}"))

    # Upload date filters
    if uploaded_after:
        query = query.filter(models.Document.uploaded_at >= uploaded_after)
    if uploaded_before:
        query = query.filter(models.Document.uploaded_at <= uploaded_before)

    documents = query.order_by(models.Document.uploaded_at.desc()).all()

    return [
        {
            "id": d.id,
            "client_phone": d.client_phone,
            "year": d.year,
            "file_name": d.file_name,
            "file_size": d.file_size,
            "uploaded_at": d.uploaded_at.isoformat(),
            "tags": [{"id": t.id, "name": t.name} for t in d.tags],
        }
        for d in documents
    ]


@router.get("/", response_model=list[schemas.Document])
def list_documents(
    db: Session = Depends(database.get_db), current_user=Depends(get_current_user_data)
):
    """List documents accessible to the current user."""
    query = db.query(models.Document).filter(models.Document.is_deleted.is_(False))

    # If client, only show their documents
    if current_user["user_type"] == "client":
        client = db.query(models.Client).filter(models.Client.id == current_user["user_id"]).first()
        query = query.filter(models.Document.client_phone == client.phone_number)

    return query.all()


@router.get("/download-token/{doc_id}")
def get_download_token(
    doc_id: int,
    db: Session = Depends(database.get_db),
    current_user=Depends(get_current_user_data),
):
    """Generate a single-use download token for a document."""
    from ca_desktop.backend.src.config import get_settings

    settings = get_settings()

    doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
    if not doc or doc.is_deleted:
        raise HTTPException(status_code=404, detail="Document not found")

    # Permissions check
    if current_user["user_type"] == "client":
        client = db.query(models.Client).filter(models.Client.id == current_user["user_id"]).first()
        if doc.client_phone != client.phone_number:
            raise HTTPException(status_code=403, detail="Access denied")

    # Generate token
    token = create_download_token(
        client_phone=doc.client_phone,
        file_path=doc.file_path,
        secret_key=settings.secret_key,
        expiry_seconds=settings.token_expiry_seconds,
    )

    return {"token": token, "download_url": f"/api/v1/documents/download/{token}"}


@router.get("/download/{token}")
def download_file(token: str, request: Request, db: Session = Depends(database.get_db)):
    """Download a file using a valid download token."""
    from ca_desktop.backend.src.config import get_settings
    from shared.crypto import verify_download_token

    settings = get_settings()

    try:
        # 1. Check if token already used (Single-use enforcement)
        if db.query(models.Download).filter(models.Download.download_token == token).first():
            raise HTTPException(status_code=403, detail="Token already used")

        # 2. Verify Token
        token_data = verify_download_token(token, settings.secret_key)

        # 3. Find Document to get ID
        doc = (
            db.query(models.Document)
            .filter(models.Document.file_path == token_data.file_path)
            .first()
        )
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        # 4. Log download access
        download_log = models.Download(
            client_phone=token_data.client_phone,
            download_type="document",
            file_id=doc.id,
            download_token=token,
            ip_address=request.client.host,
            user_agent=request.headers.get("user-agent"),
            success=True,
        )
        db.add(download_log)
        db.commit()

        # 5. Serve File
        streamer = FileStreamer()
        return streamer.get_response(token_data.file_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.warning(f"Download blocked: {str(e)}")
        raise HTTPException(status_code=403, detail="Invalid or expired download token") from e
