import time
import logging
import threading
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..dependencies import get_current_admin
from ..integrations.odoo import sync_customers, sync_products, sync_taxes
from ..notify_sync import notify_sync_result
from .. import models, schemas

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])

SYNC_NAMES = {"customers": "clientes", "products": "productos", "taxes": "impuestos"}

# Lock por tipo: evita lanzar dos syncs concurrentes del mismo tipo (doble
# click, manual + cron). El estado en curso vive en DB (sync_runs).
_run_locks = {
    "customers": threading.Lock(),
    "products": threading.Lock(),
    "taxes": threading.Lock(),
}


def _new_run(sync_type: str, name: str, triggered_by: str) -> int:
    db = SessionLocal()
    try:
        run = models.SyncRun(
            sync_type=sync_type,
            status="running",
            stage="descargando",
            total=0,
            processed=0,
            triggered_by=triggered_by,
            started_at=datetime.now(timezone.utc),
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        return run.id
    finally:
        db.close()


def _update_run(run_id: int, **kwargs) -> None:
    db = SessionLocal()
    try:
        db.query(models.SyncRun).filter(models.SyncRun.id == run_id).update(kwargs)
        db.commit()
    except Exception:
        logger.exception("No se pudo actualizar el estado del sync %s", run_id)
    finally:
        db.close()


def mark_interrupted_runs() -> None:
    """Marca como interrumpidas las corridas que quedaron 'running' (ej. un
    redeploy mientras corría el sync). Se llama al arrancar la app."""
    db = SessionLocal()
    try:
        db.query(models.SyncRun).filter(models.SyncRun.status == "running").update(
            {
                "status": "failed",
                "stage": "interrumpido",
                "error": "La app se reinició durante la sincronización",
                "finished_at": datetime.now(timezone.utc),
            }
        )
        db.commit()
    finally:
        db.close()


def _run_sync(sync_fn, sync_type: str, name: str, triggered_by: str) -> None:
    run_id = _new_run(sync_type, name, triggered_by)
    db = SessionLocal()
    start = time.time()

    def progress(stage: str | None = None, total: int | None = None, processed: int | None = None):
        updates = {}
        if stage is not None:
            updates["stage"] = stage
        if total is not None:
            updates["total"] = total
        if processed is not None:
            updates["processed"] = processed
        if updates:
            _update_run(run_id, **updates)

    try:
        logger.info("Iniciando sincronización de %s (%s)", name, triggered_by)
        sync_fn(db, progress=progress)
        elapsed = time.time() - start
        _update_run(
            run_id,
            status="completed",
            stage="completado",
            error=None,
            elapsed=elapsed,
            finished_at=datetime.now(timezone.utc),
        )
        logger.info("Sincronización de %s completada en %.1fs", name, elapsed)
    except Exception as e:
        elapsed = time.time() - start
        logger.exception("Error en sincronización de %s", name)
        _update_run(
            run_id,
            status="failed",
            stage="fallido",
            error=str(e),
            elapsed=elapsed,
            finished_at=datetime.now(timezone.utc),
        )
    finally:
        db.close()

    if triggered_by == "scheduled":
        notify_sync_result(run_id)


def enqueue_sync(sync_fn, sync_type: str, triggered_by: str = "manual") -> bool:
    """Lanza el sync en segundo plano solo si no hay uno en curso del mismo tipo.

    Devuelve True si se encoló, False si ya corría.
    """
    name = SYNC_NAMES.get(sync_type, sync_type)
    if not _run_locks[sync_type].acquire(blocking=False):
        logger.info("Sync de %s ya en curso; se omite el nuevo disparo", name)
        return False

    def task():
        try:
            _run_sync(sync_fn, sync_type, name, triggered_by)
        finally:
            _run_locks[sync_type].release()

    import threading as _t
    _t.Thread(target=task, name=f"sync-{sync_type}", daemon=True).start()
    return True


def _get_status(db: Session, sync_type: str) -> dict:
    run = (
        db.query(models.SyncRun)
        .filter(models.SyncRun.sync_type == sync_type)
        .order_by(models.SyncRun.id.desc())
        .first()
    )
    name = SYNC_NAMES.get(sync_type, sync_type)
    if run is None:
        return {"status": "idle", "name": name}
    return {
        "status": run.status,
        "name": name,
        "stage": run.stage,
        "total": run.total,
        "processed": run.processed,
        "error": run.error,
        "triggered_by": run.triggered_by,
        "started_at": run.started_at.isoformat() if run.started_at else None,
        "finished_at": run.finished_at.isoformat() if run.finished_at else None,
        "elapsed": run.elapsed,
    }


@router.get("/status/{sync_type}", response_model=schemas.SyncStatusOut)
def get_sync_status(sync_type: str, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    if sync_type not in SYNC_NAMES:
        return {"status": "idle", "name": sync_type}
    return _get_status(db, sync_type)


@router.post("/customers", status_code=202)
def trigger_sync(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    started = enqueue_sync(sync_customers, "customers")
    detail = "Sincronización de clientes iniciada en segundo plano"
    if not started:
        detail = "Sincronización de clientes ya en curso"
    return {"message": detail}


@router.post("/products", status_code=202)
def trigger_sync_products(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    started = enqueue_sync(sync_products, "products")
    detail = "Sincronización de productos iniciada en segundo plano"
    if not started:
        detail = "Sincronización de productos ya en curso"
    return {"message": detail}


@router.post("/taxes", status_code=202)
def trigger_sync_taxes(background_tasks: BackgroundTasks, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_admin)):
    started = enqueue_sync(sync_taxes, "taxes")
    detail = "Sincronización de impuestos iniciada en segundo plano"
    if not started:
        detail = "Sincronización de impuestos ya en curso"
    return {"message": detail}