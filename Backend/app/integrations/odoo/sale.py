from .client import get_odoo_connection


def create_quotation(
    partner_id: int,
    order_lines: list[dict],
    description: str = "",
    user_id: int | None = None,
    vendedor_externo_partner_id: int | None = None,
    requiere_aprobacion: bool = False,
    motivo_aprobacion: str = "",
):
    odoo = get_odoo_connection()

    # Validación en batch: 2 RPC en total en vez de N+1.
    partner_rows = odoo.env['res.partner'].search_read(
        [('id', '=', partner_id)], ['id'], limit=1
    )
    if not partner_rows:
        raise ValueError("El cliente no existe en Odoo")

    product_ids = list({line['product_id'] for line in order_lines})
    existing_ids = set()
    if product_ids:
        existing_ids = {
            row['id']
            for row in odoo.env['product.product'].search_read(
                [('id', 'in', product_ids)], ['id']
            )
        }
    missing = set(product_ids) - existing_ids
    if missing:
        raise ValueError(f"Productos no existen en Odoo: {sorted(missing)}")

    lines = []
    for line in order_lines:

        line_vals = {
            'product_id': line['product_id'],
            'product_uom_qty': line['quantity'],
            'price_unit': line['price_unit'],
            'discount': line.get('discount', 0.0),
        }

        if line.get('tax_ids'):
            line_vals['tax_ids'] = line['tax_ids']

        lines.append((0, 0, line_vals))

    order_vals = {
        'partner_id': partner_id,
        'order_line': lines,
        'state': 'draft',
    }
    if description:
        order_vals['note'] = description
    if user_id:
        order_vals['user_id'] = user_id
    if vendedor_externo_partner_id:
        order_vals['x_studio_vendedor_externo'] = vendedor_externo_partner_id

    order_vals['x_studio_requiere_aprobacion'] = bool(requiere_aprobacion)
    order_vals['x_studio_motivo_aprobacion_1'] = motivo_aprobacion

    order_id = odoo.env['sale.order'].create(order_vals)

    return order_id


def get_quotation_state(odoo_id: int) -> str | None:
    odoo = get_odoo_connection()
    sale = odoo.env['sale.order'].read(odoo_id, ['state'])
    if not sale:
        return None
    return sale[0].get('state')
