import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import FileResponse
from sqlalchemy import inspect, text

from alembic.config import Config as AlembicConfig
from alembic import command as alembic_command

from .database import Base, engine, get_db
from .auth import hash_password
from . import models
from .api import auth, products, customers, quotations, taxes, sync, health, leads
from .api.quotations import drafts_router, quotations_router
from .rate_limit import limit, setup_rate_limiter


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
        csp = "default-src 'self'; script-src 'self' 'wasm-unsafe-eval' https://www.gstatic.com; worker-src 'self' blob: https://www.gstatic.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob: https://www.gstatic.com; connect-src 'self' http: https: ws: wss:"
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

if "order_statuses" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.OrderStatus.__table__])

if "products" in inspector.get_table_names():
    prod_cols = [c["name"] for c in inspector.get_columns("products")]
    if "taxes_id" not in prod_cols:
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE products ADD COLUMN taxes_id TEXT"))

if "taxes" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.Tax.__table__])

if "quotation_drafts" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.QuotationDraft.__table__])

if "quotation_draft_lines" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.QuotationDraftLine.__table__])

if "quotations" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.Quotation.__table__])

if "leads" not in inspector.get_table_names():
    Base.metadata.create_all(bind=engine, tables=[models.Lead.__table__])

app = FastAPI(title="Belenergy API")

setup_rate_limiter(app)


@app.get("/")
async def root():
    return {"status": "ok", "app": "Belenergy API"}


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

# SPA middleware
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
            index_path = os.path.join(STATIC_DIR, "index.html")
            if os.path.isfile(index_path):
                resp = FileResponse(index_path)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=(CORS_ORIGINS != ["*"]),
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=VALID_HOSTS)

# Routers
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(customers.router)
app.include_router(taxes.router)
app.include_router(sync.router)
app.include_router(health.router)
app.include_router(drafts_router)
app.include_router(quotations_router)
app.include_router(leads.router)

# SPA catch-all (must be last)
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
