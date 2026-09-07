import logging

from .client import get_odoo_connection

logger = logging.getLogger(__name__)

# Mapeo centralizado seller_type -> industria en Odoo.
# Agregar un nuevo mapeo = agregar una entrada acá (no tocar lógica de negocio ni UI).
# Los seller_type sin industria asociada (ej. representante_general) no tienen entrada.
SELLER_TYPE_TO_INDUSTRY = {
    "representante_agro": "Agricultura",
}

# Clasificación binaria de la app: toda industria que no sea una Odoo mapeada es "General".
GENERAL_INDUSTRY_NAME = "General"

# El selector de industria solo aparece para usuarios que tienen ambos roles de venta.
SELECTOR_SELLER_TYPES = frozenset({"representante_general", "representante_agro"})

# Cache in-memory: name de industria -> odoo_id (res.partner.industry / res.industry).
_industry_cache: dict[str, int] = {}


DEFAULT_SELLER_TYPE = "representante_general"


def user_seller_types(seller_types: list[str] | None) -> list[str]:
    """Devuelve la lista de seller_types del usuario, normalizada (default general)."""
    if seller_types:
        cleaned = [s for s in seller_types if s]
        if cleaned:
            return cleaned
    return [DEFAULT_SELLER_TYPE]


def principal_seller_type(seller_types: list[str] | None) -> str:
    """Seller type principal (el primero de la lista), default general."""
    if seller_types:
        cleaned = [s for s in seller_types if s]
        if cleaned:
            return cleaned[0]
    return DEFAULT_SELLER_TYPE


def classify_industry(value: str | None) -> str:
    """Clasificación binaria: 'Agricultura' si es una industria Odoo mapeada; si no, 'General'."""
    return value if value in SELLER_TYPE_TO_INDUSTRY.values() else GENERAL_INDUSTRY_NAME


def mapped_industries(seller_types: list[str]) -> list[dict]:
    """Industrias mapeadas para los seller_types del usuario, en orden y sin duplicados."""
    result: list[dict] = []
    seen: set[str] = set()
    for st in seller_types:
        name = SELLER_TYPE_TO_INDUSTRY.get(st)
        if name and name not in seen:
            seen.add(name)
            result.append({"name": name, "seller_type": st})
    if "representante_general" in seller_types and GENERAL_INDUSTRY_NAME not in seen:
        result.append({"name": GENERAL_INDUSTRY_NAME, "seller_type": "representante_general"})
    return result


def auto_industry_for_seller_types(seller_types: list[str]) -> str | None:
    """Resuelve automáticamente la industria cuando el usuario tiene un único seller_type mapeado."""
    if len(seller_types) == 1:
        return SELLER_TYPE_TO_INDUSTRY.get(seller_types[0])
    return None


def industry_to_seller_type(industry_name: str | None) -> str | None:
    """Inverso del mapeo: industria -> seller_type. Asume 1:1 por ahora."""
    if not industry_name:
        return None
    for st, name in SELLER_TYPE_TO_INDUSTRY.items():
        if name == industry_name:
            return st
    return None


def effective_seller_type(seller_types: list[str], industry_name: str | None) -> str:
    """seller_type que se usa para evaluar descuentos.

    Si hay industria resuelta -> el seller_type que la mapea.
    Si no -> el principal del usuario.
    """
    mapped = industry_to_seller_type(industry_name)
    if mapped:
        return mapped
    if seller_types:
        return seller_types[0]
    return DEFAULT_SELLER_TYPE


INDUSTRY_MODELS = ("res.partner.industry", "res.industry")


def _search_industry(odoo, industry_name: str) -> int | None:
    """Busca el odoo_id de la industria por nombre exacto en el modelo correcto."""
    for model in INDUSTRY_MODELS:
        try:
            ids = odoo.env[model].search([("name", "=", industry_name)])
        except Exception:
            continue
        if ids:
            return int(ids[0])
    return None


def resolve_industry_id(industry_name: str | None) -> int | None:
    """Resuelve el odoo_id de la industria por nombre exacto, con cache in-memory.

    No falla si la industria no existe: loguea error claro y devuelve None.
    Los fallos no se cachean para permitir reintentos.
    """
    if not industry_name:
        return None
    if industry_name in _industry_cache:
        return _industry_cache[industry_name]
    try:
        odoo = get_odoo_connection()
        industry_id = _search_industry(odoo, industry_name)
    except Exception as e:
        logger.error("No se pudo consultar la industria '%s' en Odoo: %s", industry_name, e)
        return None
    if industry_id is None:
        logger.error("La industria '%s' no está configurada en Odoo", industry_name)
        return None
    _industry_cache[industry_name] = industry_id
    return industry_id


def clear_industry_cache() -> None:
    _industry_cache.clear()
