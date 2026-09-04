import logging
import os
import threading

import odoorpc

from ... import config

logger = logging.getLogger(__name__)

# odoorpc 0.10.1 no soporta pool_size: usa urllib opener por conexión.
# Estrategia: una conexión reutilizada (keep-alive) por thread.
# Los endpoints sync de FastAPI corren en un threadpool, así con ~10
# usuarios concurrentes hay hasta ~10 conexiones vivas, sin serializar
# todos los requests en una única conexión global (cuello de botella
# anterior) y sin cambiar los call sites de get_odoo_connection().
ODOO_TIMEOUT = int(os.getenv("ODOO_TIMEOUT", "30"))

_tls = threading.local()
_lock = threading.Lock()


def _connect():
    conn = odoorpc.ODOO(
        config.settings.ODOO_URL.replace("https://", ""),
        port=443,
        protocol='jsonrpc+ssl',
        timeout=ODOO_TIMEOUT,
    )
    conn.login(
        config.settings.ODOO_DB,
        config.settings.ODOO_USER,
        config.settings.ODOO_PASSWORD,
    )
    return conn


class OdooClient:
    def get_connection(self):
        conn = getattr(_tls, "connection", None)
        if conn is None:
            # Solo la creación se serializa; el uso posterior es por thread.
            with _lock:
                conn = getattr(_tls, "connection", None)
                if conn is None:
                    conn = _connect()
                    _tls.connection = conn
        return conn


_default_client = OdooClient()


def get_odoo_connection():
    return _default_client.get_connection()


def reset_odoo_connection():
    """Descarta la conexión del thread actual (p. ej. sesión expirada)."""
    if getattr(_tls, "connection", None) is not None:
        try:
            _tls.connection.logout()
        except Exception:
            pass
        _tls.connection = None
