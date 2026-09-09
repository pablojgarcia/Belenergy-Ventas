"""
Configuracion via variables de entorno.

⚠️ SEGURIDAD:
- En produccion (Railway) las env vars estan cifradas en reposo y transito.
- En local, el .env esta en .gitignore pero igual: no compartir el archivo.
- JWT_SECRET debe ser un valor fuerte (openssl rand -hex 32).
- ODOO_PASSWORD da acceso al ERP: rotarla periodicamente.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    ODOO_URL: str = os.getenv("ODOO_URL")
    ODOO_DB: str = os.getenv("ODOO_DB")
    ODOO_USER: str = os.getenv("ODOO_USER")
    ODOO_PASSWORD: str = os.getenv("ODOO_PASSWORD")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "9d0d3dc37a2660d64bf276215182f174049503d179104b2dff87259365cf72e0")
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    # Id de `stock.warehouse` de Odoo. Si se setea, el stock sincronizado
    # (virtual_available) se calcula para ese almacén; si no, se usa el default
    # de la compañía. Ver nota en sync.py: _product_search_context.
    ODOO_WAREHOUSE_ID: Optional[int] = None
    # Cron nocturno de sincronización (APScheduler, hora local de Buenos Aires).
    SYNC_CRON_HOUR: int = int(os.getenv("SYNC_CRON_HOUR", "2"))
    SYNC_CRON_MINUTE: int = int(os.getenv("SYNC_CRON_MINUTE", "30"))
    # Destinatarios de la notificación al terminar la corrida del cron
    # (emails separados por coma). Si no se setea, se usan los usuarios con
    # role=admin de la tabla users.
    SYNC_NOTIFY_TO: Optional[str] = None
    # Envío de las notificaciones por Resend (HTTP, sin SMTP propio). Si falta
    # la API key, los mails no se envían (solo queda el aviso en el log).
    RESEND_API_KEY: Optional[str] = os.getenv("RESEND_API_KEY")
    RESEND_FROM: str = os.getenv("RESEND_FROM", "Belenergy <notificaciones@email.belenergy.com.ar>")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../../.env")
        extra = "ignore"

settings = Settings()
