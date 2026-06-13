import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
import os

from . import models, schemas

from .config import settings

SECRET_KEY        = settings.JWT_SECRET
ALGORITHM         = os.getenv("ALGORITHM", "HS256")
EXPIRE_MINS       = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def hash_password(plain: str) -> str:
    return pwd_context.hash(plain)

def generate_jti() -> str:
    return secrets.token_urlsafe(32)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    to_encode["type"] = "access"
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=EXPIRE_MINS))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None, jti: Optional[str] = None) -> str:
    to_encode = data.copy()
    to_encode["type"] = "refresh"
    to_encode["jti"] = jti or generate_jti()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(days=REFRESH_EXPIRE_DAYS))
    to_encode["exp"] = expire
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def store_refresh_token(db: Session, user_id: int, jti: str, expires_at: datetime):
    token = models.RefreshToken(
        jti=jti,
        user_id=user_id,
        expires_at=expires_at,
    )
    db.add(token)
    db.commit()

def consume_refresh_token(db: Session, jti: str) -> bool:
    now = datetime.now(timezone.utc)
    token = db.query(models.RefreshToken).filter(
        models.RefreshToken.jti == jti,
        models.RefreshToken.used_at.is_(None),
        models.RefreshToken.expires_at > now,
    ).first()
    if not token:
        return False
    token.used_at = now
    db.commit()
    return True

def authenticate_user(db: Session, username_or_email: str, password: str):
    # Buscar por username o por email
    user = db.query(models.User).filter(
        (models.User.username == username_or_email) | (models.User.email == username_or_email)
    ).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

def decode_token(token: str) -> schemas.TokenData:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username: str = payload.get("sub")
    token_type: str = payload.get("type")
    jti: str = payload.get("jti")
    if username is None or token_type is None:
        raise JWTError("Token inválido")
    return schemas.TokenData(username=username, type=token_type, jti=jti)