"""CA management router for License Server."""

from fastapi import APIRouter, Depends, HTTPException, status
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session

from license_server.src import models, schemas
from license_server.src.database import get_db

logger = get_logger(__name__)
router = APIRouter(prefix="/ca", tags=["CA Management"])


@router.post("/", response_model=schemas.CA, status_code=status.HTTP_201_CREATED)
def register_ca(ca_in: schemas.CACreate, db: Session = Depends(get_db)):
    """Register a new Charter Accountant account."""
    db_ca = db.query(models.CA).filter(models.CA.id == ca_in.id).first()
    if db_ca:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CA with ID {ca_in.id} already exists",
        )

    db_ca = db.query(models.CA).filter(models.CA.email == ca_in.email).first()
    if db_ca:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"CA with email {ca_in.email} already exists",
        )

    db_ca = models.CA(**ca_in.dict())
    db.add(db_ca)
    db.commit()
    db.refresh(db_ca)

    logger.info(f"Registered new CA: {ca_in.id}")
    return db_ca


@router.get("/", response_model=list[schemas.CA])
def list_cas(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all registered CAs."""
    cas = db.query(models.CA).offset(skip).limit(limit).all()
    return cas


@router.get("/{ca_id}", response_model=schemas.CA)
def get_ca(ca_id: str, db: Session = Depends(get_db)):
    """Get details of a specific CA."""
    db_ca = db.query(models.CA).filter(models.CA.id == ca_id).first()
    if not db_ca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CA not found"
        )
    return db_ca


@router.patch("/{ca_id}", response_model=schemas.CA)
def update_ca(ca_id: str, ca_update: schemas.CAUpdate, db: Session = Depends(get_db)):
    """Update CA account information."""
    db_ca = db.query(models.CA).filter(models.CA.id == ca_id).first()
    if not db_ca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CA not found"
        )

    update_data = ca_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ca, field, value)

    db.commit()
    db.refresh(db_ca)
    logger.info(f"Updated CA: {ca_id}")
    return db_ca


@router.delete("/{ca_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ca(ca_id: str, db: Session = Depends(get_db)):
    """Delete (deactivate) CA account."""
    db_ca = db.query(models.CA).filter(models.CA.id == ca_id).first()
    if not db_ca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="CA not found"
        )

    # We could do a hard delete or soft delete. Let's do a soft delete by deactivating.
    db_ca.is_active = False
    db.commit()
    logger.info(f"Deactivated CA: {ca_id}")
    return None
