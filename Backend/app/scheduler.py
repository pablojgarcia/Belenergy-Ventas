"""Cron nocturno de sincronización con APScheduler.

Usa el mismo enqueue_sync que el endpoint manual (mismo lock y mismo registro
en sync_runs), con triggered_by="scheduled". Si Odoo no está configurado, el
arranque de la app no se rompe: el cron simplemente no se programa.
"""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from . import config
from .api.sync import enqueue_sync
from .integrations.odoo import sync_customers, sync_products, sync_taxes

logger = logging.getLogger(__name__)

SYNC_JOBS = {
    "customers": sync_customers,
    "products": sync_products,
    "taxes": sync_taxes,
}


def start_sync_scheduler() -> BackgroundScheduler | None:
    if not (config.settings.ODOO_URL and config.settings.ODOO_PASSWORD):
        logger.info("Odoo no configurado; cron de sincronización desactivado")
        return None

    scheduler = BackgroundScheduler(timezone="America/Argentina/Buenos_Aires")
    trigger = CronTrigger(
        hour=config.settings.SYNC_CRON_HOUR,
        minute=config.settings.SYNC_CRON_MINUTE,
    )

    def job(sync_type: str) -> None:
        started = enqueue_sync(SYNC_JOBS[sync_type], sync_type, triggered_by="scheduled")
        if not started:
            logger.warning("Cron: sync de %s ya estaba en curso; se omite", sync_type)

    for sync_type in SYNC_JOBS:
        scheduler.add_job(
            job,
            trigger,
            args=[sync_type],
            id=f"sync-{sync_type}",
            name=f"sync-{sync_type}",
            misfire_grace_time=7200,
            coalesce=True,
            max_instances=1,
        )

    scheduler.start()
    logger.info(
        "Cron de sincronización programado a las %02d:%02d ART",
        config.settings.SYNC_CRON_HOUR,
        config.settings.SYNC_CRON_MINUTE,
    )
    return scheduler