from .client import get_odoo_connection


def create_quotation(partner_id: int, order_lines: list[dict], description: str = "", vendedor_externo: str | None = None):
    odoo = get_odoo_connection()

    partner_count = odoo.env['res.partner'].search_count([('id', '=', partner_id)])
    if partner_count == 0:
        raise ValueError("El cliente no existe en Odoo")

    lines = []
    for line in order_lines:
        product_count = odoo.env['product.product'].search_count([('id', '=', line['product_id'])])
        if product_count == 0:
            raise ValueError(f"Producto ID {line['product_id']} no existe en Odoo")

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

    if vendedor_externo:
        partner_ids = odoo.env['res.users'].search([('login', '=', vendedor_externo)])
        if partner_ids:
            user = odoo.env['res.users'].read(partner_ids[0], ['partner_id'])
            if user and user.get('partner_id'):
                order_vals['x_studio_vendedor_externo_4'] = user['partner_id'][0]
        else:
            partner_ids = odoo.env['res.partner'].search([('email', '=', vendedor_externo)])
            if not partner_ids:
                partner_ids = odoo.env['res.partner'].search([('name', '=', vendedor_externo)])
            if partner_ids:
                order_vals['x_studio_vendedor_externo_4'] = partner_ids[0]

    order_id = odoo.env['sale.order'].create(order_vals)
    return order_id
