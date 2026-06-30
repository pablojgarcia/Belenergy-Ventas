from .client import get_odoo_connection


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

    vals = {
        "name": company_name or contact_name or "Sin nombre",
        "company_name": company_name,
        "email": partner_data.get("email") or "",
        "phone": partner_data.get("phone") or "",
        "street": partner_data.get("street") or "",
        "city": partner_data.get("city") or "",
        "zip": partner_data.get("zip") or "",
        "vat": partner_data.get("vat") or "",
        "customer_rank": 1,
    }

    if company_name:
        vals["company_type"] = "company"

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
            if user and user.get("partner_id"):
                vals["x_studio_vendedor_externo_4"] = user["partner_id"][0]
        else:
            partner_ids = odoo.env["res.partner"].search(
                [("email", "=", vendedor_externo)]
            )
            if not partner_ids:
                partner_ids = odoo.env["res.partner"].search(
                    [("name", "=", vendedor_externo)]
                )
            if partner_ids:
                vals["x_studio_vendedor_externo_4"] = partner_ids[0]

    partner_id = odoo.env["res.partner"].create(vals)
    return partner_id
