import time
import logging
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..dependencies import get_current_admin
from ..integrations.odoo import sync_customers, sync_products, sync_taxes
from .. import models

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


def _run_sync(sync_fn, name: str, **kwargs):
    db = SessionLocal()
    try:
        logger.info(f"Iniciando sincronización de {name}")
        start = time.time()
        sync_fn(db, **kwargs)
        elapsed = time.time() - start
        logger.info(f"Sincronización de {name} completada en {elapsed:.1f}s")
    except Exception as e:
        logger.error(f"Error en sincronización de {name}: {e}")
    finally:
        db.close()


@router.post("/customers", status_code=202)
def trigger_sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    background_tasks.add_task(_run_sync, sync_customers, "clientes")
    return {"message": "Sincronización de clientes iniciada en segundo plano"}


@router.post("/products", status_code=202)
def trigger_sync_products(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    background_tasks.add_task(_run_sync, sync_products, "productos")
    return {"message": "Sincronización de productos iniciada en segundo plano"}


@router.post("/taxes", status_code=202)
def trigger_sync_taxes(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    background_tasks.add_task(_run_sync, sync_taxes, "impuestos")
    return {"message": "Sincronización de impuestos iniciada en segundo plano"}
