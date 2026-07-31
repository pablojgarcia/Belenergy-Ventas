import time
import logging
import threading
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..dependencies import get_current_admin
from ..integrations.odoo import sync_customers, sync_products, sync_taxes
from .. import models, schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])

_sync_lock = threading.Lock()
_sync_status: dict[str, dict] = {}


def _set_status(sync_type: str, **kwargs):
    with _sync_lock:
        _sync_status[sync_type] = kwargs


def _get_status(sync_type: str) -> dict:
    with _sync_lock:
        return _sync_status.get(sync_type) or {"status": "idle", "name": sync_type, "error": None}


def _run_sync(sync_fn, sync_type: str, name: str, **kwargs):
    _set_status(
        sync_type,
        status="running",
        name=name,
        error=None,
        started_at=datetime.now(timezone.utc).isoformat(),
    )
    db = SessionLocal()
    try:
        logger.info(f"Iniciando sincronización de {name}")
        start = time.time()
        sync_fn(db, **kwargs)
        elapsed = time.time() - start
        _set_status(
            sync_type,
            status="completed",
            name=name,
            error=None,
            elapsed=elapsed,
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.info(f"Sincronización de {name} completada en {elapsed:.1f}s")
    except Exception as e:
        _set_status(
            sync_type,
            status="failed",
            name=name,
            error=str(e),
            finished_at=datetime.now(timezone.utc).isoformat(),
        )
        logger.error(f"Error en sincronización de {name}: {e}")
    finally:
        db.close()


@router.get("/status/{sync_type}", response_model=schemas.SyncStatusOut)
def get_sync_status(sync_type: str, current_user: models.User = Depends(get_current_admin)):
    return _get_status(sync_type)


@router.post("/customers", status_code=202)
def trigger_sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    background_tasks.add_task(_run_sync, sync_customers, "customers", "clientes")
    return {"message": "Sincronización de clientes iniciada en segundo plano"}


@router.post("/products", status_code=202)
def trigger_sync_products(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    background_tasks.add_task(_run_sync, sync_products, "products", "productos")
    return {"message": "Sincronización de productos iniciada en segundo plano"}


@router.post("/taxes", status_code=202)
def trigger_sync_taxes(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    background_tasks.add_task(_run_sync, sync_taxes, "taxes", "impuestos")
    return {"message": "Sincronización de impuestos iniciada en segundo plano"}
