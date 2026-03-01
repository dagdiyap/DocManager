"""Authentication dependencies and session management."""

from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from shared.utils.logging import get_logger
from sqlalchemy.orm import Session

from ca_desktop.backend.src import config, database, models

import bcrypt

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    settings = config.get_settings()
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm="HS256")
    return str(encoded_jwt)


async def get_current_user_data(
    token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)
) -> dict[str, Any]:
    """Extract user data from JWT and verify session exists in DB."""
    settings = config.get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        user_type: str = payload.get("type")
        if user_id is None or user_type is None:
            raise credentials_exception
    except JWTError as e:
        raise credentials_exception from e

    # Check session in DB
    db_session = (
        db.query(models.Session)
        .filter(
            models.Session.session_token == token,
            models.Session.user_id == int(user_id),
            models.Session.user_type == user_type,
            models.Session.expires_at > datetime.utcnow(),
        )
        .first()
    )

    if not db_session:
        raise credentials_exception

    return {"user_id": int(user_id), "user_type": user_type}


async def get_current_ca(
    current_user: dict = Depends(get_current_user_data), db: Session = Depends(database.get_db)
) -> models.User:
    """Dependency to ensure current user is a CA admin."""
    if current_user["user_type"] != "ca":
        raise HTTPException(status_code=403, detail="CA permissions required")

    user = db.query(models.User).filter(models.User.id == current_user["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_client(
    current_user: dict = Depends(get_current_user_data), db: Session = Depends(database.get_db)
) -> models.Client:
    """Dependency to ensure current user is a Client."""
    if current_user["user_type"] != "client":
        raise HTTPException(status_code=403, detail="Client permissions required")

    client = db.query(models.Client).filter(models.Client.id == current_user["user_id"]).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client
