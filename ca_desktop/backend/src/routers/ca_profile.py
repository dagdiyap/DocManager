"""CA profile and website management router."""

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from shared.utils import sanitize_filename
from shared.utils.constants import ALLOWED_FILE_EXTENSIONS
from sqlalchemy.orm import Session

from .. import schemas
from ..config import get_settings
from ..database import get_db
from ..dependencies import get_current_user_data
from ..models import CAMediaItem, CAProfile, Service, Testimonial

router = APIRouter(tags=["ca_profile"])


# Helper function to handle file uploads
def save_uploaded_file(
    file: UploadFile, ca_id: int, subfolder: str, filename: Optional[str] = None
) -> str:
    """Save uploaded file and return relative path."""
    settings = get_settings()

    if not filename:
        filename = sanitize_filename(file.filename)

    # Create uploads directory if not exists
    upload_dir = Path(settings.documents_root).parent / "uploads" / str(ca_id) / subfolder
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Save file with unique name
    file_path = upload_dir / filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    # Return relative path (always forward slashes for cross-platform DB consistency)
    return str(Path("uploads") / str(ca_id) / subfolder / filename).replace("\\", "/")


# ============ CA Profile Endpoints ============


@router.get("/ca/profile")
def get_ca_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Get CA's profile information."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can view their profile")

    ca_id = current_user.get("user_id")
    profile = db.query(CAProfile).filter(CAProfile.ca_id == ca_id).first()

    if not profile:
        # Create empty profile
        profile = CAProfile(ca_id=ca_id)
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return {
        "id": profile.id,
        "firm_name": profile.firm_name,
        "logo_path": profile.logo_file_path,
        "professional_bio": profile.professional_bio,
        "address": profile.address,
        "gstin_pan": profile.gstin_pan,
        "phone_number": profile.phone_number,
        "email": profile.email,
        "website_url": profile.website_url,
        "linkedin_url": profile.linkedin_url,
        "created_at": profile.created_at.isoformat(),
        "updated_at": profile.updated_at.isoformat(),
    }


@router.patch("/ca/profile")
def update_ca_profile(
    profile_in: schemas.CAProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Update CA's profile information."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can update their profile")

    ca_id = current_user.get("user_id")
    profile = db.query(CAProfile).filter(CAProfile.ca_id == ca_id).first()

    if not profile:
        profile = CAProfile(ca_id=ca_id)
        db.add(profile)

    update_data = profile_in.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(profile, key, value)

    db.commit()
    db.refresh(profile)

    return {
        "id": profile.id,
        "firm_name": profile.firm_name,
        "professional_bio": profile.professional_bio,
        "address": profile.address,
        "gstin_pan": profile.gstin_pan,
        "phone_number": profile.phone_number,
        "email": profile.email,
        "website_url": profile.website_url,
        "linkedin_url": profile.linkedin_url,
    }


# ============ Media Item Endpoints ============


@router.post("/ca/media")
def upload_ca_media(
    item_type: str = Form(...),  # 'carousel', 'service_background', etc.
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    order_index: int = Form(0),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Upload media item (photo, image) for CA."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can upload media")

    # Validate file type
    filename = sanitize_filename(file.filename)
    file_ext = Path(filename).suffix.lower()

    if file_ext not in ALLOWED_FILE_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File extension {file_ext} not allowed")

    ca_id = current_user.get("user_id")

    # Save file
    file_path = save_uploaded_file(file, ca_id, item_type, filename)

    # Create media item
    media = CAMediaItem(
        ca_id=ca_id,
        item_type=item_type,
        file_path=file_path,
        title=title,
        description=description,
        order_index=order_index,
        is_active=True,
    )

    db.add(media)
    db.commit()
    db.refresh(media)

    return {
        "id": media.id,
        "item_type": media.item_type,
        "file_path": media.file_path,
        "title": media.title,
        "description": media.description,
        "order_index": media.order_index,
        "is_active": media.is_active,
    }


@router.get("/ca/media")
def list_ca_media(
    item_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """List CA's media items."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can view their media")

    ca_id = current_user.get("user_id")
    query = db.query(CAMediaItem).filter(CAMediaItem.ca_id == ca_id)

    if item_type:
        query = query.filter(CAMediaItem.item_type == item_type)

    media_items = query.order_by(CAMediaItem.order_index).all()

    return [
        {
            "id": m.id,
            "item_type": m.item_type,
            "file_path": m.file_path,
            "title": m.title,
            "description": m.description,
            "order_index": m.order_index,
            "is_active": m.is_active,
        }
        for m in media_items
    ]


@router.put("/ca/media/{media_id}/order")
def reorder_ca_media(
    media_id: int,
    order_index: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Reorder media item."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can reorder media")

    ca_id = current_user.get("user_id")
    media = (
        db.query(CAMediaItem)
        .filter(
            CAMediaItem.id == media_id,
            CAMediaItem.ca_id == ca_id,
        )
        .first()
    )

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    media.order_index = order_index
    db.commit()
    db.refresh(media)

    return {
        "id": media.id,
        "order_index": media.order_index,
    }


# ============ Service Endpoints ============


@router.get("/ca/services")
def list_ca_services(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """List CA's services."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can view their services")

    ca_id = current_user.get("user_id")
    services = db.query(Service).filter(Service.ca_id == ca_id).order_by(Service.order_index).all()

    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "background_image_path": s.background_image_path,
            "order_index": s.order_index,
            "is_active": s.is_active,
        }
        for s in services
    ]


@router.post("/ca/services")
def create_ca_service(
    name: str,
    description: Optional[str] = None,
    background_image_path: Optional[str] = None,
    order_index: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Create a new service."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can create services")

    ca_id = current_user.get("user_id")

    service = Service(
        ca_id=ca_id,
        name=name,
        description=description,
        background_image_path=background_image_path,
        order_index=order_index,
        is_active=True,
    )

    db.add(service)
    db.commit()
    db.refresh(service)

    return {
        "id": service.id,
        "name": service.name,
        "description": service.description,
        "background_image_path": service.background_image_path,
        "order_index": service.order_index,
    }


@router.patch("/ca/services/{service_id}")
def update_ca_service(
    service_id: int,
    name: Optional[str] = None,
    description: Optional[str] = None,
    background_image_path: Optional[str] = None,
    order_index: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Update a service."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can update services")

    ca_id = current_user.get("user_id")
    service = (
        db.query(Service)
        .filter(
            Service.id == service_id,
            Service.ca_id == ca_id,
        )
        .first()
    )

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    if name:
        service.name = name
    if description:
        service.description = description
    if background_image_path:
        service.background_image_path = background_image_path
    if order_index is not None:
        service.order_index = order_index

    db.commit()
    db.refresh(service)

    return {"id": service.id, "name": service.name}


@router.delete("/ca/services/{service_id}")
def delete_ca_service(
    service_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Delete a service."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can delete services")

    ca_id = current_user.get("user_id")
    service = (
        db.query(Service)
        .filter(
            Service.id == service_id,
            Service.ca_id == ca_id,
        )
        .first()
    )

    if not service:
        raise HTTPException(status_code=404, detail="Service not found")

    db.delete(service)
    db.commit()

    return {"status": "success"}


# ============ Testimonial Endpoints ============


@router.get("/ca/testimonials")
def list_ca_testimonials(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """List CA's testimonials."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can view their testimonials")

    ca_id = current_user.get("user_id")
    testimonials = (
        db.query(Testimonial)
        .filter(Testimonial.ca_id == ca_id)
        .order_by(Testimonial.order_index)
        .all()
    )

    return [
        {
            "id": t.id,
            "client_name": t.client_name,
            "text": t.text,
            "rating": t.rating,
            "order_index": t.order_index,
            "is_active": t.is_active,
        }
        for t in testimonials
    ]


@router.post("/ca/testimonials")
def create_ca_testimonial(
    client_name: str,
    text: str,
    rating: Optional[int] = None,
    order_index: int = 0,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Create a new testimonial."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can create testimonials")

    ca_id = current_user.get("user_id")

    testimonial = Testimonial(
        ca_id=ca_id,
        client_name=client_name,
        text=text,
        rating=rating,
        order_index=order_index,
        is_active=True,
    )

    db.add(testimonial)
    db.commit()
    db.refresh(testimonial)

    return {
        "id": testimonial.id,
        "client_name": testimonial.client_name,
        "text": testimonial.text,
        "rating": testimonial.rating,
    }


@router.patch("/ca/testimonials/{testimonial_id}")
def update_ca_testimonial(
    testimonial_id: int,
    client_name: Optional[str] = None,
    text: Optional[str] = None,
    rating: Optional[int] = None,
    order_index: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_data),
):
    """Update a testimonial."""
    if current_user.get("user_type") != "ca":
        raise HTTPException(status_code=403, detail="Only CA can update testimonials")

    ca_id = current_user.get("user_id")
    testimonial = (
        db.query(Testimonial)
        .filter(
            Testimonial.id == testimonial_id,
            Testimonial.ca_id == ca_id,
        )
        .first()
    )

    if not testimonial:
        raise HTTPException(status_code=404, detail="Testimonial not found")

    if client_name:
        testimonial.client_name = client_name
    if text:
        testimonial.text = text
    if rating is not None:
        testimonial.rating = rating
    if order_index is not None:
        testimonial.order_index = order_index

    db.commit()
    db.refresh(testimonial)

    return {"id": testimonial.id}
