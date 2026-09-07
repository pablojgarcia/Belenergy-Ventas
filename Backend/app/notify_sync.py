"""Notificación por email (vía Odoo) al terminar la corrida del cron.

No hay infraestructura SMTP propia en el proyecto: se crea un mail.mail en Odoo
con odoorpc y Odoo lo despacha con su propio servidor de correo. Solo aplica a
corridas triggered_by="scheduled"; se notifica tanto éxito como fallo.
"""

import logging

from . import models, config
from .database import SessionLocal
from .integrations.odoo.client import get_odoo_connection

logger = logging.getLogger(__name__)

NAMES = {"customers": "clientes", "products": "productos", "taxes": "impuestos"}


def _recipients() -> list[str]:
    if config.settings.SYNC_NOTIFY_TO:
        return [e.strip() for e in config.settings.SYNC_NOTIFY_TO.split(",") if e.strip()]
    db = SessionLocal()
    try:
        return [u.email for u in db.query(models.User).filter(models.User.role == "admin").all() if u.email]
    finally:
        db.close()


def notify_sync_result(run_id: int) -> None:
    db = SessionLocal()
    try:
        run = db.query(models.SyncRun).filter(models.SyncRun.id == run_id).first()
        if not run:
            return
        sync_type, status, triggered_by = run.sync_type, run.status, run.triggered_by
        processed, error = run.processed, run.error
        elapsed = run.elapsed or 0.0
        started_at, finished_at = run.started_at, run.finished_at
    finally:
        db.close()

    if triggered_by != "scheduled" or status not in ("completed", "failed"):
        return

    name = NAMES.get(sync_type, sync_type)
    ok = status == "completed"
    subject = f"[Belenergy] Sync de {name}: {'completado' if ok else 'fallado'}"
    if ok:
        body = (
            f"Sincronización de {name} completada automáticamente.\n"
            f"Registros procesados: {processed}\n"
            f"Duración: {elapsed:.1f}s\n"
        )
    else:
        body = (
            f"La sincronización automática de {name} falló.\n"
            f"Error: {error}\n"
            f"Duración: {elapsed:.1f}s\n"
        )
    body += f"Corrida: {started_at} a {finished_at} (UTC)"

    recipients = _recipients()
    if not recipients:
        logger.warning("Sin destinatarios para notificar el resultado del sync")
        return

    try:
        odoo = get_odoo_connection()
        odoo.env["mail.mail"].create({
            "subject": subject,
            "body_html": body.replace("\n", "<br/>"),
            "email_to": recipients,
            "state": "outgoing",
        })
        logger.info("Notificación del sync %s encolada para %s", sync_type, recipients)
    except Exception:
        logger.exception("No se pudo encolar la notificación del sync en Odoo")