from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta

from .database import Base, engine, get_db
from .auth import hash_password, authenticate_user, create_access_token, EXPIRE_MINS
from .dependencies import get_current_user
from . import models, schemas
from .services.odoo_sync import sync_customers

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
    # Devuelve todos los clientes, el filtrado se hará en el frontend por seguridad de UX
    return db.query(models.Customer).all()

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
    # user_in.username contiene lo que el front envió en el campo 'username'
    # que en tu caso es el email.
    user = authenticate_user(db, user_in.username, user_in.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=EXPIRE_MINS),
    )
    return {"access_token": token, "token_type": "bearer"}

@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/health")
def health():
    return {"status": "ok"}
