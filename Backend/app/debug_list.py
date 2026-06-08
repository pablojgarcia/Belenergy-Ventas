import odoorpc
from app.config import settings

odoo = odoorpc.ODOO(settings.ODOO_URL.replace("https://", ""), port=443, protocol='jsonrpc+ssl')
odoo.login(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD)

partners = odoo.env['res.partner'].search_read([('customer_rank', '>', 0)], ['name', 'x_studio_many2one_field_2kr_1jqafs13j'], limit=20)
for p in partners:
    print(f"Cliente: {p['name']} | Vendedor: {p['x_studio_many2one_field_2kr_1jqafs13j']}")