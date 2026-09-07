import logging

from .client import get_odoo_connection

logger = logging.getLogger(__name__)


def resolve_app_user_partner_id(email: str) -> int | None:
    """Resuelve el res.partner que representa al usuario de la app (vendedor externo).

    Busca primero res.users por login (email del user de la app) y toma su partner_id.
    Si no hay user, cae a res.partner por email y luego por nombre.
    Nunca lanza: ante cualquier error loguea y devuelve None.
    """
    if not email:
        return None
    try:
        from ...services.cache_service import cache_get, cache_set

        cache_key = f"odoo_partner:{email}"
        cached = cache_get(cache_key)
        if cached is not None:
            return int(cached)
    except Exception:
        pass
    try:
        odoo = get_odoo_connection()
        user_ids = odoo.env["res.users"].search([("login", "=", email)])
        if user_ids:
            user = odoo.env["res.users"].read(user_ids[0], ["partner_id"])
            if user and user[0].get("partner_id"):
                result = int(user[0]["partner_id"][0])
                try:
                    from ...services.cache_service import cache_set

                    cache_set(f"odoo_partner:{email}", result)
                except Exception:
                    pass
                return result
        partner_ids = odoo.env["res.partner"].search([("email", "=", email)])
        if not partner_ids:
            partner_ids = odoo.env["res.partner"].search([("name", "=", email)])
        if partner_ids:
            result = int(partner_ids[0])
            try:
                from ...services.cache_service import cache_set

                cache_set(f"odoo_partner:{email}", result)
            except Exception:
                pass
            return result
        return None
    except Exception as e:
        logger.warning("No se pudo resolver el vendedor externo para '%s': %s", email, e)
        return None


def resolve_res_users_id_by_name(name: str) -> int | None:
    """Resuelve el res.users (vendedor interno) por nombre exacto.

    Toma el primero si hay varios. Nunca lanza: ante cualquier error loguea y devuelve None.
    """
    if not name:
        return None
    try:
        from ...services.cache_service import cache_get, cache_set

        cache_key = f"odoo_user:{name}"
        cached = cache_get(cache_key)
        if cached is not None:
            return int(cached)
    except Exception:
        pass
    try:
        odoo = get_odoo_connection()
        user_ids = odoo.env["res.users"].search([("name", "=", name)])
        if user_ids:
            result = int(user_ids[0])
            try:
                from ...services.cache_service import cache_set

                cache_set(f"odoo_user:{name}", result)
            except Exception:
                pass
            return result
        return None
    except Exception as e:
        logger.warning("No se pudo resolver el vendedor interno '%s': %s", name, e)
        return None


def check_vat_exists(vat: str) -> bool:
    odoo = get_odoo_connection()
    count = odoo.env["res.partner"].search_count(
        [("vat", "=", vat), ("parent_id", "=", False)]
    )
    return count > 0


def create_partner(partner_data: dict) -> int:
    odoo = get_odoo_connection()

    vat = partner_data.get("vat")
    email = partner_data.get("email")

    if vat:
        existing = odoo.env["res.partner"].search_count(
            [("vat", "=", vat), ("parent_id", "=", False)]
        )
        if existing:
            raise ValueError(
                "El cliente ya existe en Odoo con el VAT/CUIT proporcionado"
            )

    if email:
        existing = odoo.env["res.partner"].search_count(
            [("email", "=", email), ("parent_id", "=", False)]
        )
        if existing:
            raise ValueError(
                "El cliente ya existe en Odoo con el email proporcionado"
            )

    company_name = partner_data.get("company_name") or ""
    contact_name = partner_data.get("contact_name") or ""
    is_company = bool(partner_data.get("is_company", True))

    if is_company:
        vals = {
            "name": company_name or contact_name or "Sin nombre",
            "company_name": company_name,
            "company_type": "company",
        }
    else:
        vals = {
            "name": contact_name or company_name or "Sin nombre",
            "company_name": "",
            "company_type": "person",
        }

    vals.update({
        "email": partner_data.get("email") or "",
        "phone": partner_data.get("phone") or "",
        "street": partner_data.get("street") or "",
        "city": partner_data.get("city") or "",
        "zip": partner_data.get("zip") or "",
        "vat": partner_data.get("vat") or "",
        "customer_rank": 1,
    })

    state_name = partner_data.get("state")
    if state_name:
        state_ids = odoo.env["res.country.state"].search(
            [("name", "ilike", state_name)]
        )
        if state_ids:
            vals["state_id"] = state_ids[0]

    country_name = partner_data.get("country")
    if country_name:
        country_ids = odoo.env["res.country"].search(
            [("name", "ilike", country_name)]
        )
        if country_ids:
            vals["country_id"] = country_ids[0]

    vendedor_externo = partner_data.get("vendedor_externo")
    if vendedor_externo:
        partner_ids = odoo.env["res.users"].search(
            [("login", "=", vendedor_externo)]
        )
        if partner_ids:
            user = odoo.env["res.users"].read(partner_ids[0], ["partner_id"])
            if user and user[0].get("partner_id"):
                vals["x_studio_vendedor_externo"] = user[0]["partner_id"][0]
        else:
            partner_ids = odoo.env["res.partner"].search(
                [("email", "=", vendedor_externo)]
            )
            if not partner_ids:
                partner_ids = odoo.env["res.partner"].search(
                    [("name", "=", vendedor_externo)]
                )
            if partner_ids:
                vals["x_studio_vendedor_externo"] = partner_ids[0]

    industry_id = partner_data.get("industry_id")
    if industry_id:
        vals["industry_id"] = industry_id

    partner_id = odoo.env["res.partner"].create(vals)
    return partner_id
