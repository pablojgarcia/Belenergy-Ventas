"""Tests del scheduler: el cron diario y el full semanal de productos.

El punto que más importa acá es que los dos jobs NO se pisen. Si compartieran
hora, `enqueue_sync` hace pasar solo al segundo (mismo sync_type, mismo lock)
y el full se perdería todas las semanas sin dejar rastro.
"""
import os

os.environ["DISABLE_RATE_LIMIT"] = "true"

from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from app import scheduler as sched


def _start(overrides=None, enqueue_return=True):
    """Arranca el scheduler con todo fakificado y devuelve el mock del scheduler.

    Los patches se mantienen vigentes (no en un `with` que ya cerro) porque los
    jobs se invocan DESPUES de arrancar: si no, el patch de enqueue_sync ya
    salio de alcance y el job llama al enqueue_sync real.
    """
    overrides = overrides or {}
    real = sched.config.settings
    values = {
        "ODOO_URL": real.ODOO_URL,
        "ODOO_PASSWORD": real.ODOO_PASSWORD,
        "SYNC_CRON_HOUR": real.SYNC_CRON_HOUR,
        "SYNC_CRON_MINUTE": real.SYNC_CRON_MINUTE,
        "SYNC_FULL_WEEKDAY": real.SYNC_FULL_WEEKDAY,
        "SYNC_FULL_HOUR": real.SYNC_FULL_HOUR,
        "SYNC_FULL_MINUTE": real.SYNC_FULL_MINUTE,
    }
    values.update(overrides)
    ns = SimpleNamespace(**values)
    fake_sched = MagicMock()
    enqueued = []

    def record(sync_fn, sync_type, triggered_by="manual"):
        enqueued.append((sync_fn, sync_type, triggered_by))
        return enqueue_return

    p1 = patch.object(sched.config, "settings", ns)
    p2 = patch.object(sched, "BackgroundScheduler", return_value=fake_sched)
    p3 = patch.object(sched, "enqueue_sync", side_effect=record)
    for p in (p1, p2, p3):
        p.start()
    sched.start_sync_scheduler()
    _cleanup.append((p1, p2, p3))
    return fake_sched, enqueued


_cleanup = []


def teardown_function(_function):
    for p in _cleanup:
        for q in p:
            q.stop()
    _cleanup.clear()


def test_registers_daily_jobs_and_weekly_full():
    fake_sched, _ = _start()
    ids = [c.kwargs["id"] for c in fake_sched.add_job.call_args_list]
    assert "sync-customers" in ids
    assert "sync-products" in ids
    assert "sync-taxes" in ids
    assert "sync-products-full" in ids


def test_weekly_full_default_time_differs_from_daily_default():
    """Si coincidieran por default, el lock haria que uno se salte siempre.

    Se prueba sobre los defaults reales de la config, que es donde importa:
    es el estado en el que va a quedar la produccion.
    """
    from app import config as app_config

    daily = (app_config.settings.SYNC_CRON_HOUR, app_config.settings.SYNC_CRON_MINUTE)
    full = (app_config.settings.SYNC_FULL_HOUR, app_config.settings.SYNC_FULL_MINUTE)
    assert daily != full, (
        "el full semanal comparte hora con el diario: enqueue_sync usa el mismo "
        "lock por sync_type, asi que uno de los dos se omite sin avisar"
    )


def test_weekly_full_trigger_is_on_its_configured_day_and_time():
    fake_sched, _ = _start({"SYNC_FULL_WEEKDAY": 6, "SYNC_FULL_HOUR": 4,
                            "SYNC_FULL_MINUTE": 0})
    triggers = {}
    for c in fake_sched.add_job.call_args_list:
        fields = {f.name: str(f) for f in c.args[1].fields}
        triggers[c.kwargs["id"]] = fields

    full = triggers["sync-products-full"]
    # APScheduler normaliza day_of_week a su indice numerico: sun = 6
    assert full["day_of_week"] == "6"
    assert full["hour"] == "4"
    assert full["minute"] == "0"


def test_weekly_full_calls_sync_products_with_force_full():
    fake_sched, enqueued = _start()
    full_call = next(c for c in fake_sched.add_job.call_args_list
                     if c.kwargs["id"] == "sync-products-full")
    full_call.args[0]()

    assert len(enqueued) == 1
    sync_fn, sync_type, triggered_by = enqueued[0]
    assert sync_type == "products"
    # triggered_by propio para poder distinguirlo en el historial
    assert triggered_by == "scheduled_full"
    # force_full=True debe venir en los bound args del partial
    assert sync_fn.keywords["force_full"] is True


def test_daily_products_job_stays_incremental():
    """El diario NO debe ser full: el full es solo el semanal."""
    fake_sched, enqueued = _start()
    daily_call = next(c for c in fake_sched.add_job.call_args_list
                      if c.kwargs["id"] == "sync-products")
    daily_call.args[0]("products")

    assert enqueued[0][1] == "products"
    assert enqueued[0][2] == "scheduled"
    # El sync diario se encola como función suelta, sin force_full
    assert not hasattr(enqueued[0][0], "keywords")


def test_weekly_full_skipped_when_one_already_running():
    """Si ya hay un sync en curso, el lock lo omite (no duplica trabajo)."""
    fake_sched, enqueued = _start(enqueue_return=False)
    full_call = next(c for c in fake_sched.add_job.call_args_list
                     if c.kwargs["id"] == "sync-products-full")
    # no debe romper aunque enqueue_sync devuelva False (lock tomado)
    full_call.args[0]()
    assert len(enqueued) == 1  # se intento, pero el lock decidio


def test_scheduler_not_started_without_odoo():
    fake_sched, _ = _start({"ODOO_URL": None, "ODOO_PASSWORD": None})
    assert fake_sched.add_job.call_count == 0
