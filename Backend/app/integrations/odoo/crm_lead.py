from .client import get_odoo_connection


def check_cuit_exists(cuit: str) -> bool:
    odoo = get_odoo_connection()
    count = odoo.env["res.partner"].search_count(
        [("vat", "=", cuit), ("parent_id", "=", False)]
    )
    return count > 0


def check_crm_lead_status(odoo_crm_lead_id: int) -> dict:
    try:
        odoo = get_odoo_connection()
        found = odoo.env["crm.lead"].search([("id", "=", odoo_crm_lead_id)])
        if not found:
            return {"status": "not_found"}

        lead = odoo.env["crm.lead"].browse(odoo_crm_lead_id)
        stage = lead.stage_id
        return {
            "status": "found",
            "stage_id": stage.id if stage else None,
            "stage_name": stage.name if stage else "",
            "is_won": bool(stage.is_won) if stage else False,
            "active": bool(lead.active),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


def create_crm_lead(lead_data: dict) -> int:
    odoo = get_odoo_connection()

    vals = {
        "name": lead_data.get("company_name") or lead_data.get("contact_name") or "Lead sin nombre",
        "contact_name": lead_data.get("contact_name") or "",
        "email_from": lead_data.get("email") or "",
        "phone": lead_data.get("phone") or "",
        "street": lead_data.get("street") or "",
        "city": lead_data.get("city") or "",
        "zip": lead_data.get("zip") or "",
        "description": (lead_data.get("notes") or "") + ("\nCUIT: " + lead_data.get("vat", "") if lead_data.get("vat") else ""),
        "partner_name": lead_data.get("company_name") or lead_data.get("contact_name") or "",
        "type": "opportunity",
    }

    state_name = lead_data.get("state")
    if state_name:
        state_ids = odoo.env["res.country.state"].search(
            [("name", "ilike", state_name)]
        )
        if state_ids:
            vals["state_id"] = state_ids[0]

    country_name = lead_data.get("country")
    if country_name:
        country_ids = odoo.env["res.country"].search(
            [("name", "ilike", country_name)]
        )
        if country_ids:
            vals["country_id"] = country_ids[0]

    vendedor_externo = lead_data.get("vendedor_externo")
    if vendedor_externo:
        user_ids = odoo.env["res.users"].search(
            [("login", "=", vendedor_externo)]
        )
        if user_ids:
            user = odoo.env["res.users"].read(user_ids[0], ["partner_id"])
            if user and user.get("partner_id"):
                vals["x_studio_vendedor_de_contacto"] = user["partner_id"][0]
        else:
            partner_ids = odoo.env["res.partner"].search(
                [("email", "=", vendedor_externo)]
            )
            if not partner_ids:
                partner_ids = odoo.env["res.partner"].search(
                    [("name", "=", vendedor_externo)]
                )
            if partner_ids:
                vals["x_studio_vendedor_de_contacto"] = partner_ids[0]

    vendedor_interno = lead_data.get("vendedor_interno")
    if vendedor_interno:
        interno_user_ids = odoo.env["res.users"].search(
            [("login", "=", vendedor_interno)]
        )
        if not interno_user_ids:
            interno_user_ids = odoo.env["res.users"].search(
                [("name", "=", vendedor_interno)]
            )
        if interno_user_ids:
            vals["user_id"] = interno_user_ids[0]

    lead_id = odoo.env["crm.lead"].create(vals)
    return lead_id
