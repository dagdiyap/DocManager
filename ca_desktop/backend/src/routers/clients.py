"""Client management router for CA Dashboard."""

from ca_desktop.backend.src import database, models, schemas
from ca_desktop.backend.src.config import get_settings
from ca_desktop.backend.src.dependencies import get_current_ca, get_password_hash
from ca_desktop.backend.src.services.audit_service import log_client_created, log_client_updated, log_client_deleted
from ca_desktop.backend.src.services.email_service import send_welcome_email
from ca_desktop.backend.src.utils.invite import (
    generate_client_password,
    generate_qr_code,
    generate_whatsapp_share_url,
)
from ca_desktop.backend.src.utils.bulk_upload import (
    parse_excel_file,
    parse_text_file,
    deduplicate_clients,
)
from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, status
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session
from typing import List

logger = get_logger(__name__)
router = APIRouter(prefix="/clients", tags=["Client Management"])


@router.post("/", response_model=schemas.ClientWithInvite, status_code=status.HTTP_201_CREATED)
def create_client(
    client_in: schemas.ClientCreate,
    request: Request,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """Add a new client and return invite card with QR code and WhatsApp share URL."""
    # Check if client already exists
    db_client = (
        db.query(models.Client).filter(models.Client.phone_number == client_in.phone_number).first()
    )
    if db_client:
        raise HTTPException(status_code=400, detail="Client with this phone number already exists")

    # Use provided password or auto-generate
    plain_password = client_in.password if client_in.password else generate_client_password()
    
    # Create client
    new_client = models.Client(
        phone_number=client_in.phone_number,
        name=client_in.name,
        email=client_in.email,
        client_type=client_in.client_type if hasattr(client_in, 'client_type') else None,
        password_hash=get_password_hash(plain_password),
        is_active=True,
    )
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    # Create client directory
    from pathlib import Path
    settings = get_settings()
    client_dir = Path(settings.documents_root) / client_in.phone_number
    client_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created directory for client: {client_dir}")

    # Generate invite data
    settings = get_settings()
    ca_slug = current_ca.slug or current_ca.username
    ca_display_name = current_ca.display_name or current_ca.username
    
    # Construct portal URL
    # In production, this should use the actual domain from settings
    portal_url = f"https://www.example.com/ca-{ca_slug}/home"
    
    # Generate QR code
    qr_code_base64 = generate_qr_code(portal_url)
    
    # Generate WhatsApp share URL
    whatsapp_url = generate_whatsapp_share_url(
        portal_url=portal_url,
        username=client_in.phone_number,
        password=plain_password,
        ca_name=ca_display_name,
    )
    
    # Send welcome email if client has email
    if client_in.email:
        email_sent = send_welcome_email(
            client_email=client_in.email,
            client_name=client_in.name,
            portal_url=portal_url,
            username=client_in.phone_number,
            password=plain_password,
            ca_name=ca_display_name,
        )
        if email_sent:
            logger.info(f"Welcome email sent to {client_in.email}")
        else:
            logger.warning(f"Failed to send welcome email to {client_in.email}")
    
    # Log audit event
    log_client_created(
        db=db,
        ca_username=current_ca.username,
        client_phone=client_in.phone_number,
        ip_address=request.client.host if request.client else None,
    )
    
    logger.info(f"CA {current_ca.username} created client {client_in.phone_number}")
    
    # Return client with invite data
    client_directory = str(client_dir.absolute())
    
    return {
        "client": new_client,
        "invite": {
            "portal_url": portal_url,
            "username": client_in.phone_number,
            "password": plain_password,
            "qr_code_base64": qr_code_base64,
            "whatsapp_share_url": whatsapp_url,
            "client_directory": client_directory,
        }
    }


@router.post("/bulk-upload")
async def bulk_upload_clients(
    file: UploadFile = File(...),
    request: Request = None,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """
    Bulk upload clients from Excel (.xlsx) or text (.txt) file.
    
    Excel format: Automatically detects phone, name, and email columns.
    Text format: One client per line - phone,name,email OR just phone number.
    
    Returns summary of created clients, duplicates, and errors.
    """
    # Validate file type
    filename = file.filename.lower()
    if not (filename.endswith('.xlsx') or filename.endswith('.txt')):
        raise HTTPException(
            status_code=400,
            detail="Invalid file type. Please upload .xlsx or .txt file"
        )
    
    # Read file content
    file_content = await file.read()
    
    # Parse file based on type
    if filename.endswith('.xlsx'):
        clients_data, parse_errors = parse_excel_file(file_content)
    else:
        clients_data, parse_errors = parse_text_file(file_content)
    
    if not clients_data and parse_errors:
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {'; '.join(parse_errors[:3])}")
    
    # Deduplicate within file
    clients_data, file_duplicates = deduplicate_clients(clients_data)
    
    # Process each client
    created = []
    skipped_existing = []
    errors = []
    
    settings = get_settings()
    ca_display_name = current_ca.display_name or current_ca.username
    
    for client_data in clients_data:
        try:
            phone = client_data["phone_number"]
            
            # Check if client already exists in database
            existing = db.query(models.Client).filter(models.Client.phone_number == phone).first()
            if existing:
                skipped_existing.append(phone)
                continue
            
            # Generate password
            plain_password = generate_client_password()
            
            # Create client
            new_client = models.Client(
                phone_number=phone,
                name=client_data["name"],
                email=client_data.get("email"),
                password_hash=get_password_hash(plain_password),
                is_active=True,
            )
            db.add(new_client)
            db.flush()  # Get ID without committing
            
            # Log audit event
            log_client_created(
                db=db,
                ca_username=current_ca.username,
                client_phone=phone,
                ip_address=request.client.host if request and request.client else None,
            )
            
            created.append({
                "phone_number": phone,
                "name": client_data["name"],
                "password": plain_password,
            })
            
            # Send welcome email if email provided
            if client_data.get("email") and settings.resend_api_key:
                portal_url = f"{settings.base_url}/ca-{current_ca.slug}/home"
                send_welcome_email(
                    to_email=client_data["email"],
                    client_name=client_data["name"],
                    portal_url=portal_url,
                    username=phone,
                    password=plain_password,
                    ca_name=ca_display_name,
                )
            
        except Exception as e:
            errors.append(f"{phone}: {str(e)}")
            logger.error(f"Failed to create client {phone}: {e}")
    
    # Commit all successful creations
    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    logger.info(f"Bulk upload by {current_ca.username}: {len(created)} created, {len(skipped_existing)} skipped, {len(errors)} errors")
    
    return {
        "success": True,
        "summary": {
            "total_in_file": len(clients_data) + file_duplicates,
            "file_duplicates": file_duplicates,
            "unique_clients": len(clients_data),
            "created": len(created),
            "skipped_existing": len(skipped_existing),
            "errors": len(errors),
        },
        "created_clients": created,
        "skipped_phones": skipped_existing,
        "errors": errors + parse_errors,
    }


@router.get("/", response_model=list[schemas.Client])
def list_clients(
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """List all clients for the CA."""
    return db.query(models.Client).all()


@router.get("/{phone_number}", response_model=schemas.Client)
def get_client(
    phone_number: str,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """Get specific client details."""
    client = db.query(models.Client).filter(models.Client.phone_number == phone_number).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.patch("/{phone_number}", response_model=schemas.Client)
def update_client(
    phone_number: str,
    client_update: schemas.ClientUpdate,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """Update client information."""
    db_client = db.query(models.Client).filter(models.Client.phone_number == phone_number).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    update_data = client_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)

    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/{phone_number}", status_code=status.HTTP_204_NO_CONTENT)
def delete_client(
    phone_number: str,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(get_current_ca),
):
    """Deactivate a client."""
    db_client = db.query(models.Client).filter(models.Client.phone_number == phone_number).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client not found")

    db_client.is_active = False
    db.commit()
    return None
