import odoorpc
from app.config import settings

def debug_odoo_customer():
    # Conexión directa
    odoo = odoorpc.ODOO(settings.ODOO_URL.replace("https://", ""), port=443, protocol='jsonrpc+ssl')
    odoo.login(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD)
    
    # Buscar el cliente específico
    partner_ids = odoo.env['res.partner'].search([('name', '=', 'Pablo Javier Garcia')])
    if not partner_ids:
        print("No se encontró el cliente 'Pablo Javier Garcia'")
        return
        
    p = odoo.env['res.partner'].browse(partner_ids[0])
    
    print("--- Estructura del registro ---")
    print(f"ID: {p.id}")
    print(f"Name: {p.name}")
    print(f"Email: {p.email}")
    print(f"x_studio_email_vendedor_externo: {p.x_studio_email_vendedor_externo} (Tipo: {type(p.x_studio_email_vendedor_externo)})")
    
    # Listar atributos disponibles si es necesario
    # print(dir(p))

if __name__ == "__main__":
    debug_odoo_customer()
