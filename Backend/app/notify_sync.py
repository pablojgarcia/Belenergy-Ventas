"""Notificación por email (vía Resend) al terminar la corrida del cron.

Odoo no tiene SMTP saliente configurado, así que la notificación sale por la
API HTTP de Resend (stdlib urllib, sin dependencia nueva). Solo aplica a
corridas triggered_by="scheduled"; se notifica tanto éxito como fallo. Sin
RESEND_API_KEY los mails no se envían (queda el aviso en el log).
"""

import json
import logging
import urllib.error
import urllib.request

from . import config, models
from .database import SessionLocal

logger = logging.getLogger(__name__)

NAMES = {"customers": "clientes", "products": "productos", "taxes": "impuestos"}

RESEND_API = "https://api.resend.com/emails"


def _recipients() -> list[str]:
    if config.settings.SYNC_NOTIFY_TO:
        return [e.strip() for e in config.settings.SYNC_NOTIFY_TO.split(",") if e.strip()]
    db = SessionLocal()
    try:
        return [u.email for u in db.query(models.User).filter(models.User.role == "admin").all() if u.email]
    finally:
        db.close()


def _send_email(to: list[str], subject: str, html: str) -> None:
    if not config.settings.RESEND_API_KEY:
        logger.warning("RESEND_API_KEY no configurada; no se envía la notificación del sync")
        return
    payload = json.dumps({
        "from": config.settings.RESEND_FROM,
        "to": to,
        "subject": subject,
        "html": html,
    }).encode()
    req = urllib.request.Request(
        RESEND_API,
        data=payload,
        headers={
            "Authorization": f"Bearer {config.settings.RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            logger.info("Notificación del sync enviada a %s (HTTP %s)", to, resp.status)
    except urllib.error.HTTPError as e:
        # Mensajes de error de Resend dentro del body (p. ej. dominio sin verificar)
        logger.error("Resend rechazó la notificación (HTTP %s): %s", e.code, e.read().decode(errors="replace")[:300])
    except Exception:
        logger.exception("No se pudo enviar la notificación del sync por Resend")


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
            f"Sincronización de {name} completada automáticamente.<br/>"
            f"Registros procesados: {processed}<br/>"
            f"Duración: {elapsed:.1f}s<br/>"
        )
    else:
        body = (
            f"La sincronización automática de {name} falló.<br/>"
            f"Error: {error}<br/>"
            f"Duración: {elapsed:.1f}s<br/>"
        )
    body += f"Corrida: {started_at} a {finished_at} (UTC)"

    recipients = _recipients()
    if not recipients:
        logger.warning("Sin destinatarios para notificar el resultado del sync")
        return
    _send_email(recipients, subject, body)