import base64
import odoorpc
from sqlalchemy.orm import Session
from .. import models, config

def get_odoo_connection():
    odoo = odoorpc.ODOO(config.settings.ODOO_URL.replace("https://", ""), port=443, protocol='jsonrpc+ssl')
    odoo.login(config.settings.ODOO_DB, config.settings.ODOO_USER, config.settings.ODOO_PASSWORD)
    return odoo

def sync_customers(db: Session):
    odoo = get_odoo_connection()
    
    fields = [
        'id', 'name', 'email', 'phone', 'mobile', 'company_name',
        'street', 'city',
        'state_id', 'zip', 'country_id', 'vat', 'user_id',
        'x_studio_vendedor_externo', 'website'
    ]
    
    print("Buscando clientes en Odoo...")
    partners_data = odoo.env['res.partner'].search_read([('customer_rank', '>', 0)], fields)
    print(f"Encontrados {len(partners_data)} clientes. Procesando...")

    vendedor_ids = set()
    interno_ids = set()
    for p in partners_data:
        vendedor = p.get('x_studio_vendedor_externo')
        if vendedor and isinstance(vendedor, (list, tuple)):
            vendedor_ids.add(vendedor[0])
        interno = p.get('user_id')
        if interno and isinstance(interno, (list, tuple)):
            interno_ids.add(interno[0])

    vendedores_map = {}
    if vendedor_ids:
        vendedores_info = odoo.env['res.partner'].read(list(vendedor_ids), ['name', 'email'])
        for v in vendedores_info:
            vendedores_map[v['id']] = v['email'] or v['name'] or ""

    internos_map = {}
    if interno_ids:
        internos_info = odoo.env['res.users'].read(list(interno_ids), ['name'])
        for u in internos_info:
            internos_map[u['id']] = u['name'] or ""

    for p in partners_data:
        vendedor = p.get('x_studio_vendedor_externo')
        salesperson_val = None
        if vendedor and isinstance(vendedor, (list, tuple)):
            salesperson_val = vendedores_map.get(vendedor[0])

        interno = p.get('user_id')
        interno_val = None
        if interno and isinstance(interno, (list, tuple)):
            interno_val = internos_map.get(interno[0])
        
        # Diccionario explícito
        customer_data = {
            "odoo_id": int(p['id']),
            "name": str(p.get('name') or ""),
            "email": str(p.get('email') or ""),
            "phone": str(p.get('phone') or ""),
            "mobile": str(p.get('mobile') or ""),
            "company_name": str(p.get('company_name') or ""),
            "street": str(p.get('street') or ""),
            "city": str(p.get('city') or ""),
            "state": str(p.get('state_id')[1] if p.get('state_id') else ""),
            "zip": str(p.get('zip') or ""),
            "country": str(p.get('country_id')[1] if p.get('country_id') else ""),
            "vat": str(p.get('vat') or ""),
            "cuit": str(p.get('vat') or ""),
            "vendedor_interno": interno_val or "",
            "contact_name": str(p.get('name') or ""),
            "contact_email": str(p.get('email') or ""),
            "salesperson_id": salesperson_val,
            "website": str(p.get('website') or "")
        }
        
        # Validar inserción/actualización
        customer = db.query(models.Customer).filter(models.Customer.odoo_id == p['id']).first()
        if customer:
            for key, value in customer_data.items():
                setattr(customer, key, value)
        else:
            customer = models.Customer(**customer_data)
            db.add(customer)
    
    db.commit()
    print("Sincronización completada en la base de datos.")

def sync_products(db: Session):
    odoo = get_odoo_connection()

    fields = [
        'id', 'name', 'default_code', 'barcode', 'list_price',
        'standard_price', 'type', 'categ_id', 'uom_id',
        'description_sale', 'active', 'sale_ok', 'image_1920'
    ]

    print("Buscando productos en Odoo...")
    products_data = odoo.env['product.template'].search_read([('active', '=', True)], fields)
    print(f"Encontrados {len(products_data)} productos. Procesando...")

    for p in products_data:
        raw_image = p.get('image_1920')
        image_bytes = base64.b64decode(raw_image) if raw_image else None

        product_data = {
            "odoo_id": int(p['id']),
            "name": str(p.get('name') or ""),
            "default_code": str(p.get('default_code') or ""),
            "barcode": str(p.get('barcode') or ""),
            "list_price": float(p.get('list_price') or 0.0),
            "standard_price": float(p.get('standard_price') or 0.0),
            "type": str(p.get('type') or "product"),
            "categ_id": str(p.get('categ_id')[1] if p.get('categ_id') else ""),
            "uom_id": str(p.get('uom_id')[1] if p.get('uom_id') else ""),
            "description_sale": str(p.get('description_sale') or ""),
            "active": bool(p.get('active', True)),
            "sale_ok": bool(p.get('sale_ok', True)),
            "image": image_bytes,
        }

        product = db.query(models.Product).filter(models.Product.odoo_id == p['id']).first()
        if product:
            for key, value in product_data.items():
                setattr(product, key, value)
        else:
            product = models.Product(**product_data)
            db.add(product)

    db.commit()
    print("Sincronización de productos completada.")
