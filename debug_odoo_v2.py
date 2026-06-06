import odoorpc
from app.config import settings

def debug_odoo_customer():
    odoo = odoorpc.ODOO(settings.ODOO_URL.replace("https://", ""), port=443, protocol='jsonrpc+ssl')
    odoo.login(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD)
    
    partner_ids = odoo.env['res.partner'].search([('name', '=', 'Pablo Javier Garcia')])
    if not partner_ids:
        print("No se encontró el cliente 'Pablo Javier Garcia'")
        return
        
    p = odoo.env['res.partner'].browse(partner_ids[0])
    
    print("--- Estructura del registro ---")
    print(f"ID: {p.id}")
    print(f"Name: {p.name}")
    # Probamos el campo correcto
    field_name = 'x_studio_many2one_field_2kr_1jqafs13j'
    vendedor = getattr(p, field_name, "Campo no encontrado")
    
    print(f"{field_name}: {vendedor}")
    if hasattr(vendedor, 'name'):
        print(f"Vendedor Name: {vendedor.name}")
    if hasattr(vendedor, 'email'):
        print(f"Vendedor Email: {vendedor.email}")

if __name__ == "__main__":
    debug_odoo_customer()
