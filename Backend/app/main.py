import os
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from datetime import timedelta, datetime, timezone

from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

from .database import Base, engine, get_db
from .auth import hash_password, authenticate_user, create_access_token, create_refresh_token, decode_token, store_refresh_token, consume_refresh_token, generate_jti, EXPIRE_MINS, REFRESH_EXPIRE_DAYS
from .dependencies import get_current_user, get_current_admin
from . import models, schemas
from fastapi.responses import Response, FileResponse
from .services.odoo_sync import sync_customers, sync_products, get_odoo_connection
from .services.odoo_sale import create_quotation


STATIC_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "static"))


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        csp = "default-src 'self'; script-src 'self' 'wasm-unsafe-eval' https://www.gstatic.com; worker-src 'self' blob: https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https://www.gstatic.com; connect-src 'self' https://www.gstatic.com https://fonts.gstatic.com"
        response.headers["Content-Security-Policy"] = csp
        return response

# Migraciones con Alembic (fallback a create_all si no hay alembic.cfg)
_alembic_cfg_path = os.path.join(os.path.dirname(__file__), "..", "alembic.ini")
if os.path.isfile(_alembic_cfg_path):
    try:
        _cfg = AlembicConfig(_alembic_cfg_path)
        alembic_command.upgrade(_cfg, "head")
    except Exception:
        Base.metadata.create_all(bind=engine)
else:
    Base.metadata.create_all(bind=engine)

# Migraciones livianas para columnas faltantes en DB existentes
inspector = inspect(engine)
if "users" in inspector.get_table_names():
    cols = [c["name"] for c in inspector.get_columns("users")]
    if "role" not in cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR DEFAULT 'vendedor'"))

if "customers" in inspector.get_table_names():
    cust_cols = [c["name"] for c in inspector.get_columns("customers")]
    if "mobile" not in cust_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE customers ADD COLUMN mobile VARCHAR"))
    if "company_name" not in cust_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE customers ADD COLUMN company_name VARCHAR"))
    if "cuit" not in cust_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE customers ADD COLUMN cuit VARCHAR"))
    if "vendedor_interno" not in cust_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE customers ADD COLUMN vendedor_interno VARCHAR"))

if "contacts" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.Contact.__table__])

if "orders" in inspector.get_table_names():
    ord_cols = [c["name"] for c in inspector.get_columns("orders")]
    if "vendedor_externo" not in ord_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE orders ADD COLUMN vendedor_externo VARCHAR"))

if "order_statuses" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.OrderStatus.__table__])

app = FastAPI(title="Auth API")

if os.path.isdir(STATIC_DIR):
    SPA_EXCLUDE = {"/docs", "/openapi.json", "/redoc", "/health"}

    @app.middleware("http")
    async def spa_middleware(request: Request, call_next):
        accept = request.headers.get("accept", "")
        if (
            request.method == "GET"
            and "text/html" in accept
            and "." not in request.url.path
            and request.url.path not in SPA_EXCLUDE
        ):
            resp = FileResponse(os.path.join(STATIC_DIR, "index.html"))
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            resp.headers["Vary"] = "Accept"
            return resp
        return await call_next(request)

CORS_ORIGINS_ENV = os.getenv("CORS_ORIGINS")
if CORS_ORIGINS_ENV:
    CORS_ORIGINS = [o.strip() for o in CORS_ORIGINS_ENV.split(",")]
else:
    CORS_ORIGINS = ["*"]

VALID_HOSTS = os.getenv("VALID_HOSTS", "").split(",") if os.getenv("VALID_HOSTS") else ["*"]

# Seed: asegurar que existe al menos un admin
_seed_db = next(get_db())
try:
    _admin_exists = _seed_db.query(models.User).filter(models.User.role == "admin").count() > 0
    if not _admin_exists:
        _first = _seed_db.query(models.User).order_by(models.User.id).first()
        if _first:
            _first.role = "admin"
            _first.hashed_password = hash_password("admin123")
            _seed_db.commit()
        _admin_user = _seed_db.query(models.User).filter(models.User.username == "admin").first()
        if _admin_user:
            _admin_user.role = "admin"
            _admin_user.hashed_password = hash_password("admin123")
            _seed_db.commit()
        else:
            _admin = models.User(
                email="admin@belenergy.com",
                username="admin",
                name="Admin",
                role="admin",
                hashed_password=hash_password("admin123"),
            )
            _seed_db.add(_admin)
            _seed_db.commit()
except Exception as e:
    print(f"Seed error: {e}")
finally:
    _seed_db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=(CORS_ORIGINS != ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=VALID_HOSTS)

@app.post("/sync/customers", status_code=200)
def trigger_sync(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    try:
        sync_customers(db)
        return {"message": "Sincronización completada"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al sincronizar clientes: {str(e)}")

@app.get("/customers", response_model=list[schemas.CustomerOut])
def get_customers(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    return db.query(models.Customer).filter(
        models.Customer.salesperson_id.in_([current_user.email, current_user.name])
    ).all()

@app.get("/customers/{customer_id}/contacts", response_model=list[schemas.ContactOut])
def get_customer_contacts(customer_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    return db.query(models.Contact).filter(models.Contact.customer_id == customer_id).all()

@app.post("/sync/products", status_code=200)
def trigger_sync_products(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    try:
        sync_products(db)
        return {"message": "Sincronización de productos completada"}
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error al sincronizar productos: {str(e)}")

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

if os.getenv("DISABLE_RATE_LIMIT") != "true":
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(429, _rate_limit_exceeded_handler)
else:
    limiter = None

def limit(rate: str):
    if limiter is not None:
        return limiter.limit(rate)
    return lambda func: func

@app.post("/auth/register", response_model=schemas.UserOut, status_code=201)
@limit("5/minute")
def register(request: Request, user_in: schemas.UserCreate, db: Session = Depends(get_db)):
    first_user = db.query(models.User).count() == 0

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
        admin = db.query(models.User).filter(
            models.User.username == token_data.username,
            models.User.role == "admin",
        ).first()
        if not admin:
            raise HTTPException(403, "Se requieren permisos de administrador")

    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(400, "El email ya está registrado")
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(400, "El nombre de usuario ya existe")

    role = "admin" if first_user else user_in.role

    user = models.User(
        email=user_in.email,
        username=user_in.username,
        name=user_in.name,
        role=role,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/auth/login", response_model=schemas.Token)
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


@app.post("/auth/refresh", response_model=schemas.Token)
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


@app.get("/auth/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.post("/orders/quotation", status_code=201)
def create_quotation_endpoint(
    order_in: schemas.OrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    customer = db.query(models.Customer).filter(models.Customer.odoo_id == order_in.partner_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")
    if customer.salesperson_id not in [current_user.email, current_user.name]:
        raise HTTPException(status_code=403, detail="No tenés permiso para crear presupuestos para este cliente")

    try:
        odoo_id = create_quotation(
            partner_id=order_in.partner_id,
            order_lines=[line.model_dump() for line in order_in.order_line],
            description=order_in.description,
            vendedor_externo=customer.salesperson_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=502, detail="Error al comunicarse con Odoo")

    total = sum(
        line.quantity * line.price_unit * (1 - line.discount / 100)
        for line in order_in.order_line
    )

    order = models.Order(
        odoo_id=odoo_id,
        client_id=customer.id,
        client_name=customer.name,
        amount_total=total,
        state="draft",
        user_id=current_user.id,
        description=order_in.description,
        vendedor_externo=customer.salesperson_id,
    )
    db.add(order)
    db.flush()

    status_entry = models.OrderStatus(
        order_id=order.id,
        status="creada",
        changed_by=current_user.id,
    )
    db.add(status_entry)
    db.commit()
    db.refresh(order)

    return order

@app.get("/orders", response_model=list[schemas.OrderOut])
def list_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
    state: Optional[str] = None,
):
    q = db.query(models.Order).filter(models.Order.user_id == current_user.id)
    if state:
        q = q.filter(models.Order.state == state)
    return q.all()

@app.get("/orders/{order_id}", response_model=schemas.OrderOut)
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso para ver este presupuesto")
    return order

@app.post("/orders/{order_id}/sync-status")
def sync_order_status(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso")

    odoo = get_odoo_connection()
    sales = odoo.env["sale.order"].read(order.odoo_id, ["state"])
    if not sales:
        raise HTTPException(status_code=502, detail="No se pudo leer la orden en Odoo")
    odoo_state = sales[0]["state"]

    app_status_map = {
        "sent": "cotizacion_enviada",
        "sale": "orden_de_venta",
        "cancel": "cancelada",
    }
    app_status = app_status_map.get(odoo_state, odoo_state)

    last_status = (
        db.query(models.OrderStatus)
        .filter(models.OrderStatus.order_id == order.id)
        .order_by(models.OrderStatus.changed_at.desc())
        .first()
    )

    if last_status is None or last_status.status != app_status:
        entry = models.OrderStatus(
            order_id=order.id,
            status=app_status,
            changed_by=current_user.id,
        )
        db.add(entry)
        order.state = odoo_state
        db.commit()
        return {"synced": True, "previous": last_status.status if last_status else None, "current": app_status}

    return {"synced": False, "current": app_status}

@app.get("/orders/{order_id}/statuses", response_model=list[schemas.OrderStatusOut])
def get_order_statuses(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    if order.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tenés permiso")
    return db.query(models.OrderStatus).filter(models.OrderStatus.order_id == order.id).order_by(models.OrderStatus.changed_at.desc()).all()

@app.get("/health")
def health():
    return {"status": "ok"}


if os.path.isdir(STATIC_DIR):
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        file_path = os.path.normpath(os.path.join(STATIC_DIR, full_path or ""))
        if file_path != STATIC_DIR and not file_path.startswith(STATIC_DIR + os.sep):
            resp = FileResponse(os.path.join(STATIC_DIR, "index.html"))
            resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return resp
        if os.path.isfile(file_path):
            resp = FileResponse(file_path)
            if full_path == "index.html":
                resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            return resp
        resp = FileResponse(os.path.join(STATIC_DIR, "index.html"))
        resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return resp
