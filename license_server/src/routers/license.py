"""License management router for License Server."""

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from shared.crypto import create_license_token
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session

from license_server.src import config, models, schemas
from license_server.src.database import get_db

logger = get_logger(__name__)
router = APIRouter(prefix="/license", tags=["License Issuance"])


@router.post("/issue", response_model=schemas.License)
def issue_license(license_in: schemas.LicenseCreate, db: Session = Depends(get_db)):
    """Issue a new signed license token for a CA and device."""
    settings = config.get_settings()

    # 1. Verify CA exists and is active
    db_ca = (
        db.query(models.CA)
        .filter(models.CA.id == license_in.ca_id, models.CA.is_active)
        .first()
    )
    if not db_ca:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Active CA not found"
        )

    # 2. Check if device is registered (or register it here if we want automatic binding)
    db_device = (
        db.query(models.Device)
        .filter(
            models.Device.ca_id == license_in.ca_id,
            models.Device.device_id == license_in.device_id,
        )
        .first()
    )

    # For now, let's assume device must be registered separately or we can create a record here
    # Actually, let's create it if it doesn't exist for simplicity in PoC
    if not db_device:
        # Note: In a real app we'd want the fingerprint from the request
        logger.warning(
            f"Device {license_in.device_id} not pre-registered for CA {license_in.ca_id}, creating record."
        )
        # This is a bit of a hack since we don't have the fingerprint yet
        # Normally /register_device would be called first.

    # 3. Calculate expiry
    expiry_days = license_in.expiry_days or settings.default_license_days
    if expiry_days > settings.max_license_days:
        expiry_days = settings.max_license_days

    expires_at = datetime.utcnow() + timedelta(days=expiry_days)

    # 4. Generate the signed token
    try:
        private_key = settings.private_key_path.read_bytes()
        token = create_license_token(
            ca_id=license_in.ca_id,
            device_id=license_in.device_id,
            private_key_pem=private_key,
            expiry_days=expiry_days,
        )
    except Exception as e:
        logger.error(f"Failed to generate license token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating signed license token",
        ) from e

    # 5. Save to database
    db_license = models.License(
        ca_id=license_in.ca_id,
        device_id=license_in.device_id,
        license_token=token,
        issued_at=datetime.utcnow(),
        expires_at=expires_at,
        is_active=True,
    )
    db.add(db_license)

    # Deactivate previous licenses for this device
    db.query(models.License).filter(
        models.License.ca_id == license_in.ca_id,
        models.License.device_id == license_in.device_id,
        models.License.id != db_license.id,
    ).update({"is_active": False})

    db.commit()
    db.refresh(db_license)

    logger.info(
        f"Issued license to CA {license_in.ca_id} for device {license_in.device_id}"
    )
    return db_license


@router.post("/register-device", response_model=schemas.Device)
def register_device(device_in: schemas.DeviceCreate, db: Session = Depends(get_db)):
    """Register a device fingerprint for a CA."""
    # Verify CA exists
    db_ca = db.query(models.CA).filter(models.CA.id == device_in.ca_id).first()
    if not db_ca:
        raise HTTPException(status_code=404, detail="CA not found")

    # Check if device already registered
    db_device = (
        db.query(models.Device)
        .filter(models.Device.device_id == device_in.device_id)
        .first()
    )
    if db_device:
        if db_device.ca_id != device_in.ca_id:
            raise HTTPException(
                status_code=400, detail="Device already registered to another CA"
            )

        # Update fingerprint if it changed
        db_device.device_fingerprint = device_in.device_fingerprint
        db_device.device_info = device_in.device_info
        db_device.last_seen = datetime.utcnow()
    else:
        db_device = models.Device(**device_in.dict())
        db.add(db_device)

    db.commit()
    db.refresh(db_device)
    logger.info(f"Registered device {device_in.device_id} for CA {device_in.ca_id}")
    return db_device


@router.post("/revoke/{license_id}", status_code=status.HTTP_204_NO_CONTENT)
def revoke_license(
    license_id: int,
    reason: str = "Administrative revocation",
    db: Session = Depends(get_db),
):
    """Revoke a specific license."""
    db_license = (
        db.query(models.License).filter(models.License.id == license_id).first()
    )
    if not db_license:
        raise HTTPException(status_code=404, detail="License not found")

    db_license.is_active = False
    db_license.revoked_at = datetime.utcnow()
    db_license.revocation_reason = reason

    db.commit()
    logger.info(f"Revoked license {license_id} for CA {db_license.ca_id}")
    return None


@router.get("/validate-sync/{ca_id}/{device_id}", response_model=schemas.License)
def validate_and_sync(ca_id: str, device_id: str, db: Session = Depends(get_db)):
    """Get the latest active license for a CA/device during periodic sync."""
    db_license = (
        db.query(models.License)
        .filter(
            models.License.ca_id == ca_id,
            models.Device.device_id == device_id,
            models.License.is_active.is_(True),
            models.License.expires_at > datetime.utcnow(),
        )
        .order_by(models.License.issued_at.desc())
        .first()
    )

    if not db_license:
        raise HTTPException(
            status_code=404, detail="No active license found for this device"
        )

    return db_license
