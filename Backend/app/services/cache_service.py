"""Cache Redis con fallback silencioso (sin Redis = sin cache, sin errores).

Variables de entorno:
- REDIS_URL: ej. redis://default:...@redis.railway.internal:6379
- CACHE_DEFAULT_TTL: segundos (default 60)
"""

DEFAULT_TTL = 60

import json
import logging
import os

logger = logging.getLogger(__name__)

_redis = None
_sentinel = object()


def get_redis():
    global _redis
    if _redis is None:
        url = os.getenv("REDIS_URL")
        if not url:
            _redis = False
            return None
        try:
            import redis

            _redis = redis.from_url(url, decode_responses=True)
        except Exception as e:
            logger.warning("Redis no disponible (%s). Cache deshabilitado.", e)
            _redis = False
            return None
    return _redis or None


def cache_get(key: str):
    r = get_redis()
    if r is None:
        return None
    try:
        val = r.get(key)
        return json.loads(val) if val is not None else None
    except Exception as e:
        logger.debug("cache_get %s falló: %s", key, e)
        return None


def cache_set(key: str, value, ttl: int | None = None) -> bool:
    r = get_redis()
    if r is None:
        return False
    try:
        ttl = ttl if ttl is not None else int(os.getenv("CACHE_DEFAULT_TTL", str(DEFAULT_TTL)))
        r.setex(key, ttl, json.dumps(value, default=str))
        return True
    except Exception as e:
        logger.debug("cache_set %s falló: %s", key, e)
        return False


def cache_invalidate(key: str) -> None:
    r = get_redis()
    if r is None:
        return
    try:
        r.delete(key)
    except Exception:
        pass


def cache_invalidate_pattern(pattern: str) -> int:
    """Borra todas las claves que matcheen el patrón. Devuelve cantidad borrada."""
    r = get_redis()
    if r is None:
        return 0
    try:
        count = 0
        for key in r.scan_iter(match=pattern, count=200):
            r.delete(key)
            count += 1
        return count
    except Exception as e:
        logger.debug("cache_invalidate_pattern %s falló: %s", pattern, e)
        return 0
