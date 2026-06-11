from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta

from .database import Base, engine, get_db
from .auth import hash_password, authenticate_user, create_access_token, create_refresh_token, decode_token, EXPIRE_MINS, REFRESH_EXPIRE_DAYS
from .dependencies import get_current_user
from . import models, schemas
from fastapi.responses import Response
from .services.odoo_sync import sync_customers, sync_products

# Crea tablas al iniciar (en producción usar Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/sync/customers", status_code=200)
def trigger_sync(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sync_customers(db)
    return {"message": "Sincronización completada"}

@app.get("/customers", response_model=list[schemas.CustomerOut])
def get_customers(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Customer).filter(
        models.Customer.salesperson_id.in_([current_user.email, current_user.name])
    ).all()

@app.post("/sync/products", status_code=200)
def trigger_sync_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    sync_products(db)
    return {"message": "Sincronización de productos completada"}

@app.get("/products", response_model=list[schemas.ProductOut])
def get_products(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    search: Optional[str] = None,
    categ_id: Optional[str] = None,
    active: Optional[bool] = True,
    sale_ok: Optional[bool] = True,
):
    q = db.query(models.Product).filter(
        models.Product.active == active,
        models.Product.sale_ok == sale_ok,
    )
    if search:
        q = q.filter(models.Product.name.ilike(f"%{search}%"))
    if categ_id:
        q = q.filter(models.Product.categ_id == categ_id)
    return q.all()

@app.get("/products/{product_id}", response_model=schemas.ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@app.get("/products/{product_id}/image")
def get_product_image_endpoint(product_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    product = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not product or not product.image:
        raise HTTPException(status_code=404, detail="Imagen no disponible")
    return Response(content=product.image, media_type="image/png")

@app.post("/auth/register", response_model=schemas.UserOut, status_code=201)
def register(user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(400, "El email ya está registrado")
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(400, "El nombre de usuario ya existe")
    user = models.User(
        email=user_in.email,
        username=user_in.username,
        name=user_in.name,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=schemas.Token)
def login(user_in: schemas.UserLogin, db: Session = Depends(get_db)):
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
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@app.post("/auth/refresh", response_model=schemas.Token)
def refresh(token_in: schemas.TokenRefresh, db: Session = Depends(get_db)):
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

    user = db.query(models.User).filter(
        models.User.username == token_data.username
    ).first()
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo",
        )

    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=EXPIRE_MINS),
    )
    refresh_token = create_refresh_token(
        data={"sub": user.username},
        expires_delta=timedelta(days=REFRESH_EXPIRE_DAYS),
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }

@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/health")
def health():
    return {"status": "ok"}
