from .. import config
from .odoo_sync import get_odoo_connection


def create_quotation(partner_id: int, order_lines: list[dict], description: str = ""):
    odoo = get_odoo_connection()

    partner = odoo.env['res.partner'].browse(partner_id)
    if not partner.exists():
        raise ValueError("El cliente no existe en Odoo")

    lines = []
    for line in order_lines:
        product = odoo.env['product.product'].browse(line['product_id'])
        if not product.exists():
            raise ValueError(f"Producto ID {line['product_id']} no existe en Odoo")

        line_vals = {
            'product_id': line['product_id'],
            'product_uom_qty': line['quantity'],
            'price_unit': line['price_unit'],
            'discount': line.get('discount', 0.0),
        }
        if line.get('tax_id'):
            line_vals['tax_id'] = [(6, 0, line['tax_id'])]

        lines.append((0, 0, line_vals))

    order_vals = {
        'partner_id': partner_id,
        'order_line': lines,
        'state': 'draft',
    }
    if description:
        order_vals['note'] = description

    order_id = odoo.env['sale.order'].create(order_vals)
    return order_id
