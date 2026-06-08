import odoorpc
from app.config import settings

def debug_odoo_products():
    odoo = odoorpc.ODOO(settings.ODOO_URL.replace("https://", ""), port=443, protocol='jsonrpc+ssl')
    odoo.login(settings.ODOO_DB, settings.ODOO_USER, settings.ODOO_PASSWORD)

    fields = [
        'id', 'name', 'default_code', 'barcode', 'list_price',
        'standard_price', 'type', 'categ_id', 'uom_id',
        'description_sale', 'active', 'sale_ok'
    ]

    products = odoo.env['product.template'].search_read([('active', '=', True)], fields)

    print(f"--- {len(products)} productos activos encontrados ---")
    for p in products[:10]:
        print(f"\nID: {p['id']}")
        print(f"  Name: {p.get('name')}")
        print(f"  Default Code: {p.get('default_code')}")
        print(f"  Barcode: {p.get('barcode')}")
        print(f"  List Price: {p.get('list_price')}")
        print(f"  Standard Price: {p.get('standard_price')}")
        print(f"  Type: {p.get('type')}")
        print(f"  Categ ID: {p.get('categ_id')} (type: {type(p.get('categ_id'))})")
        print(f"  UOM ID: {p.get('uom_id')} (type: {type(p.get('uom_id'))})")
        print(f"  Desc Sale: {str(p.get('description_sale') or '')[:80]}")
        print(f"  Active: {p.get('active')}")
        print(f"  Sale OK: {p.get('sale_ok')}")

if __name__ == "__main__":
    debug_odoo_products()
