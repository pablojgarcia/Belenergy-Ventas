from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone

from ..database import get_db
from ..auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    decode_token,
    store_refresh_token,
    consume_refresh_token,
    generate_jti,
    EXPIRE_MINS,
    REFRESH_EXPIRE_DAYS,
)
from ..dependencies import get_current_user, get_current_admin
from ..rate_limit import limit
from ..repositories.user_repository import UserRepository
from .. import models, schemas

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=schemas.UserOut, status_code=201)
@limit("5/minute")
def register(request: Request, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    first_user = user_repo.count() == 0

    if not first_user:
        auth = request.headers.get("Authorization") or ""
        if not auth.startswith("Bearer "):
            raise HTTPException(403, "Se requieren permisos de administrador")
        try:
            token_data = decode_token(auth.removeprefix("Bearer "))
        except Exception:
            raise HTTPException(403, "Se requieren permisos de administrador")
        if token_data.type != "access":
            raise HTTPException(403, "Se requieren permisos de administrador")
        admin = user_repo.get_by_username(token_data.username)
        if not admin or admin.role != "admin":
            raise HTTPException(403, "Se requieren permisos de administrador")

    if user_repo.get_by_email(user_in.email):
        raise HTTPException(400, "El email ya está registrado")
    if user_repo.get_by_username(user_in.username):
        raise HTTPException(400, "El nombre de usuario ya existe")

    role = "admin" if first_user else user_in.role

    user = models.User(
        email=user_in.email,
        username=user_in.username,
        name=user_in.name,
        role=role,
        hashed_password=hash_password(user_in.password),
    )
    user_repo.create(user)
    user_repo.save(user)
    db.refresh(user)
    return user


@router.post("/login", response_model=schemas.Token)
@limit("5/minute")
def login(request: Request, user_in: schemas.UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, user_in.username, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=EXPIRE_MINS),
    )
    jti = generate_jti()
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS),
        jti=jti,
    )
    store_refresh_token(
        db,
        user_id=user.id,
        jti=jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=schemas.Token)
@limit("5/minute")
def refresh(request: Request, token_in: schemas.TokenRefresh, db: Session = Depends(get_db)):
    try:
        token_data = decode_token(token_in.refresh_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado",
        )

    if token_data.type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tipo de token incorrecto",
        )

    if not token_data.jti or not consume_refresh_token(db, token_data.jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token ya utilizado o inválido",
        )

    user_repo = UserRepository(db)
    user = user_repo.get_by_username(token_data.username)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=EXPIRE_MINS),
    )
    jti = generate_jti()
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS),
        jti=jti,
    )
    store_refresh_token(
        db,
        user_id=user.id,
        jti=jti,
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_EXPIRE_DAYS),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user
