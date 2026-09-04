from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..database import get_db  # noqa: F401 (mantiene firma consistente con otros routers)
from ..dependencies import get_current_admin
from .. import models
from ..services.cache_service import (
    cache_invalidate,
    cache_invalidate_pattern,
    get_redis,
)

router = APIRouter(prefix="/admin/cache", tags=["admin-cache"])

# Prefijos que usa el backend. Invalidar todo = los 3 patrones.
KNOWN_PREFIXES = ("discount_rules:*", "odoo_partner:*", "odoo_user:*")


class InvalidateBody(BaseModel):
    # Patrón Redis (ej. "discount_rules:*") o clave exacta.
    pattern: str | None = None
    key: str | None = None


@router.post("/invalidate")
def invalidate_cache(
    body: InvalidateBody | None = None,
    current_user: models.User = Depends(get_current_admin),
):
    if body and body.key:
        cache_invalidate(body.key)
        return {"invalidated": 1, "key": body.key}

    if body and body.pattern:
        count = cache_invalidate_pattern(body.pattern)
        return {"invalidated": count, "pattern": body.pattern}

    total = 0
    for prefix in KNOWN_PREFIXES:
        total += cache_invalidate_pattern(prefix)
    return {"invalidated": total, "patterns": list(KNOWN_PREFIXES)}


@router.get("/status")
def cache_status(current_user: models.User = Depends(get_current_admin)):
    r = get_redis()
    if r is None:
        return {"available": False}
    try:
        info = r.info("keyspace")
        return {"available": True, "keyspace": info}
    except Exception:
        return {"available": False}
