"""Authentication router for CA Desktop."""

from datetime import datetime, timedelta
from typing import Optional, Union

from ca_desktop.backend.src import database, dependencies, models, schemas
from ca_desktop.backend.src.dependencies import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from ca_desktop.backend.src.utils.invite import generate_ca_slug, validate_slug
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordRequestForm
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session

logger = get_logger(__name__)
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
def register(user_in: schemas.UserCreate, db: Session = Depends(database.get_db)) -> models.User:
    """Register the first CA admin user (Bootstrap)."""
    # Check if any CA user already exists
    existing_ca = db.query(models.User).first()
    if existing_ca:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="CA user already exists. Registration is disabled.",
        )

    # Check email/username uniqueness (though the first check covers most cases, race conditions might exist)
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Generate slug from display_name or username
    slug = None
    if user_in.display_name:
        slug = generate_ca_slug(user_in.display_name)
        
        # Ensure slug uniqueness
        counter = 1
        original_slug = slug
        while db.query(models.User).filter(models.User.slug == slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
    
    # Create user
    new_user = models.User(
        username=user_in.username,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        display_name=user_in.display_name,
        slug=slug,
        created_at=datetime.utcnow(),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info(f"Bootstrap CA user created: {new_user.username}, slug: {slug}")
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(
    db: Session = Depends(database.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> dict[str, str]:
    """Unified login for CA and Client."""
    logger.info(f"Login attempt for username: {form_data.username}")
    
    # 1. Try CA first
    user: Union[models.User, models.Client, None] = (
        db.query(models.User).filter(models.User.username == form_data.username).first()
    )
    user_type = "ca"

    if not user:
        logger.info(f"User not found as CA, trying client lookup")
        # 2. Try Client
        user = (
            db.query(models.Client).filter(models.Client.phone_number == form_data.username).first()
        )
        user_type = "client"

    if not user:
        logger.warning(f"Login failed: user not found - {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    logger.info(f"User found: {user.username if hasattr(user, 'username') else user.phone_number}, type: {user_type}")
    
    # Verify password
    password_valid = verify_password(form_data.password, user.password_hash)
    logger.info(f"Password verification result: {password_valid}")
    
    if not password_valid:
        logger.warning(f"Login failed: incorrect password for {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Create Access Token
    access_token = create_access_token(data={"sub": str(user.id), "type": user_type})

    # 4. Save session to DB
    new_session = models.Session(
        session_token=access_token,
        user_type=user_type,
        user_id=user.id,
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )
    db.add(new_session)

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    logger.info(f"Successful login: {form_data.username} ({user_type})")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user_type,
    }


@router.get("/audit-logs", response_model=list[schemas.AuditLog])
def list_audit_logs(
    limit: int = Query(50, le=100),
    offset: int = Query(0, ge=0),
    event_type: Optional[str] = None,
    db: Session = Depends(database.get_db),
    current_ca: models.User = Depends(dependencies.get_current_ca),
) -> list[models.AuditLog]:
    """List audit logs (CA only)."""
    query = db.query(models.AuditLog)

    if event_type:
        query = query.filter(models.AuditLog.event_type == event_type)

    logs = query.order_by(models.AuditLog.created_at.desc()).offset(offset).limit(limit).all()
    return logs


@router.post("/logout")
def logout(
    current_user=Depends(dependencies.get_current_user_data),
    db: Session = Depends(database.get_db),
    token: str = Depends(dependencies.oauth2_scheme),
) -> dict[str, str]:
    """Invalidate session."""
    db.query(models.Session).filter(models.Session.session_token == token).delete()
    db.commit()
    return {"detail": "Successfully logged out"}
