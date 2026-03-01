"""Public website endpoints (no authentication required)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import CAMediaItem, CAProfile, Service, Testimonial, User

router = APIRouter(tags=["public"])


def get_ca_by_username(username: str, db: Session) -> Optional[User]:
    """Get CA user by username."""
    return db.query(User).filter(User.username == username).first()


def get_ca_by_slug(slug: str, db: Session) -> Optional[User]:
    """Get CA user by slug."""
    return db.query(User).filter(User.slug == slug).first()


@router.get("/public/ca/{ca_username}/profile")
def get_public_ca_profile(
    ca_username: str,
    db: Session = Depends(get_db),
):
    """Get public CA profile (no auth required)."""
    ca_user = get_ca_by_username(ca_username, db)
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA not found")

    profile = db.query(CAProfile).filter(CAProfile.ca_id == ca_user.id).first()

    if not profile:
        return {
            "ca_username": ca_username,
            "firm_name": None,
            "professional_bio": None,
            "address": None,
            "phone_number": None,
            "email": None,
        }

    return {
        "ca_username": ca_username,
        "firm_name": profile.firm_name,
        "logo_path": profile.logo_file_path,
        "professional_bio": profile.professional_bio,
        "address": profile.address,
        "phone_number": profile.phone_number,
        "email": profile.email,
        "website_url": profile.website_url,
    }


@router.get("/public/ca/{ca_username}/media")
def get_public_ca_media(
    ca_username: str,
    item_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """Get public CA media (carousel, service images, etc.)."""
    ca_user = get_ca_by_username(ca_username, db)
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA not found")

    query = db.query(CAMediaItem).filter(
        CAMediaItem.ca_id == ca_user.id,
        CAMediaItem.is_active,  # noqa: E712
    )

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
        }
        for m in media_items
    ]


@router.get("/public/ca/{ca_username}/services")
def get_public_ca_services(
    ca_username: str,
    db: Session = Depends(get_db),
):
    """Get public CA services list."""
    ca_user = get_ca_by_username(ca_username, db)
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA not found")

    services = (
        db.query(Service)
        .filter(
            Service.ca_id == ca_user.id,
            Service.is_active,  # noqa: E712
        )
        .order_by(Service.order_index)
        .all()
    )

    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "background_image_path": s.background_image_path,
            "order_index": s.order_index,
        }
        for s in services
    ]


@router.get("/public/ca/{ca_username}/testimonials")
def get_public_ca_testimonials(
    ca_username: str,
    db: Session = Depends(get_db),
):
    """Get public CA testimonials."""
    ca_user = get_ca_by_username(ca_username, db)
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA not found")

    testimonials = (
        db.query(Testimonial)
        .filter(
            Testimonial.ca_id == ca_user.id,
            Testimonial.is_active,  # noqa: E712
        )
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
        }
        for t in testimonials
    ]


@router.get("/public/ca-slug/{ca_slug}")
def get_ca_by_slug_endpoint(
    ca_slug: str,
    db: Session = Depends(get_db),
):
    """Get CA profile by slug for multi-tenant routing."""
    ca_user = get_ca_by_slug(ca_slug, db)
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA not found")

    profile = db.query(CAProfile).filter(CAProfile.ca_id == ca_user.id).first()
    
    # Get services
    services = db.query(Service).filter(
        Service.ca_id == ca_user.id,
        Service.is_active == True
    ).order_by(Service.order_index).all()
    
    # Get testimonials
    testimonials = db.query(Testimonial).filter(
        Testimonial.ca_id == ca_user.id,
        Testimonial.is_active == True
    ).order_by(Testimonial.order_index).all()

    return {
        "slug": ca_user.slug,
        "display_name": ca_user.display_name,
        "username": ca_user.username,
        "profile": {
            "firm_name": profile.firm_name if profile else None,
            "logo_path": profile.logo_file_path if profile else None,
            "professional_bio": profile.professional_bio if profile else None,
            "address": profile.address if profile else None,
            "phone_number": profile.phone_number if profile else None,
            "email": profile.email if profile else None,
            "website_url": profile.website_url if profile else None,
        } if profile else None,
        "services": [
            {
                "id": s.id,
                "title": s.name,
                "description": s.description or ""
            } for s in services
        ],
        "testimonials": [
            {
                "id": t.id,
                "client_name": t.client_name,
                "content": t.text,
                "rating": t.rating or 5
            } for t in testimonials
        ],
    }


@router.get("/public/ca-slug/{ca_slug}/portal")
def get_ca_portal_metadata(
    ca_slug: str,
    db: Session = Depends(get_db),
):
    """Get CA portal metadata for client login page customization."""
    ca_user = get_ca_by_slug(ca_slug, db)
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA not found")

    profile = db.query(CAProfile).filter(CAProfile.ca_id == ca_user.id).first()

    return {
        "slug": ca_slug,
        "display_name": ca_user.display_name or ca_user.username,
        "firm_name": profile.firm_name if profile else None,
        "logo_path": profile.logo_file_path if profile else None,
        "portal_url": f"/ca-{ca_slug}/home",
    }


@router.get("/public/ca/{ca_username}/clients/{client_id}")
def get_client_portal_link(
    ca_username: str,
    client_id: str,
    db: Session = Depends(get_db),
):
    """Get client portal link (shows client needs to login)."""
    ca_user = get_ca_by_username(ca_username, db)
    if not ca_user:
        raise HTTPException(status_code=404, detail="CA not found")

    return {
        "ca_username": ca_username,
        "client_id": client_id,
        "portal_url": f"/client/{client_id}",
        "message": "Use the portal link to access your documents",
    }
