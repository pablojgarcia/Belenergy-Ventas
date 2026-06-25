import json
import base64
from sqlalchemy.orm import Session
from ... import models
from .client import get_odoo_connection


def sync_customers(db: Session):
    odoo = get_odoo_connection()

    fields = [
        'id', 'name', 'email', 'phone', 'company_name',
        'street', 'city',
        'state_id', 'zip', 'country_id', 'vat', 'user_id',
        'x_studio_vendedor_externo', 'website'
    ]

    print("Buscando clientes en Odoo...")
    partners_data = odoo.env['res.partner'].search_read([], fields)
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

        customer_data = {
            "odoo_id": int(p['id']),
            "name": str(p.get('name') or ""),
            "email": str(p.get('email') or ""),
            "phone": str(p.get('phone') or ""),
            "company_name": str(p.get('company_name') or ""),
            "street": str(p.get('street') or ""),
            "city": str(p.get('city') or ""),
            "state": str(p.get('state_id')[1] if p.get('state_id') else ""),
            "zip": str(p.get('zip') or ""),
            "country": str(p.get('country_id')[1] if p.get('country_id') else ""),
            "vat": str(p.get('vat') or ""),
            "cuit": str(p.get('vat') or ""),
            "vendedor_interno": interno_val or "",
            "salesperson_id": salesperson_val,
            "website": str(p.get('website') or "")
        }

        customer = db.query(models.Customer).filter(models.Customer.odoo_id == p['id']).first()
        if customer:
            for key, value in customer_data.items():
                setattr(customer, key, value)
        else:
            customer = models.Customer(**customer_data)
            db.add(customer)

    db.commit()
    print("Sincronización completada en la base de datos.")

    print("Sincronizando contactos...")
    partner_ids = [p['id'] for p in partners_data]
    contact_fields = ['id', 'name', 'email', 'phone', 'parent_id']
    contacts_data = odoo.env['res.partner'].search_read(
        [('parent_id', 'in', partner_ids), ('type', '=', 'contact')],
        contact_fields
    )
    print(f"Encontrados {len(contacts_data)} contactos.")

    odoo_to_customer = {c.odoo_id: c.id for c in db.query(models.Customer).all()}

    for c in contacts_data:
        parent = c.get('parent_id')
        if not parent or not isinstance(parent, (list, tuple)):
            continue
        parent_odoo_id = parent[0]
        local_customer_id = odoo_to_customer.get(parent_odoo_id)
        if not local_customer_id:
            continue

        contact_data = {
            "odoo_id": int(c['id']),
            "customer_id": local_customer_id,
            "name": str(c.get('name') or ""),
            "email": str(c.get('email') or ""),
            "phone": str(c.get('phone') or ""),
        }

        contact = db.query(models.Contact).filter(
            models.Contact.odoo_id == c['id']
        ).first()
        if contact:
            for key, value in contact_data.items():
                setattr(contact, key, value)
        else:
            contact = models.Contact(**contact_data)
            db.add(contact)

    synced_odoo_ids = {c['id'] for c in contacts_data if c.get('parent_id') and isinstance(c['parent_id'], (list, tuple))}
    db.query(models.Contact).filter(
        models.Contact.customer_id.in_(odoo_to_customer.values()),
        ~models.Contact.odoo_id.in_(synced_odoo_ids),
    ).delete(synchronize_session=False)

    db.commit()
    print("Sincronización de contactos completada.")


def sync_taxes(db: Session):
    odoo = get_odoo_connection()

    tax_fields = ['id', 'name', 'amount', 'type_tax_use']
    taxes_data = odoo.env['account.tax'].search_read([], tax_fields)
    print(f"Sincronizando {len(taxes_data)} impuestos...")

    for t in taxes_data:
        tax_data = {
            "odoo_id": int(t['id']),
            "name": str(t.get('name') or f"Impuesto {t['id']}"),
            "amount": float(t.get('amount') or 0.0),
            "type_tax_use": str(t.get('type_tax_use') or 'sale'),
        }
        tax = db.query(models.Tax).filter(models.Tax.odoo_id == t['id']).first()
        if tax:
            for k, v in tax_data.items():
                setattr(tax, k, v)
        else:
            db.add(models.Tax(**tax_data))

    db.commit()
    print("Sincronización de impuestos completada.")


def sync_products(db: Session):
    odoo = get_odoo_connection()

    fields = [
        'id', 'name', 'default_code', 'barcode', 'list_price',
        'standard_price', 'type', 'categ_id', 'uom_id',
        'description_sale', 'active', 'sale_ok', 'image_1920',
        'taxes_id'
    ]

    print("Cargando precios de lista USD Lista de Precios...")
    pricelist_items = odoo.env['product.pricelist.item'].search_read(
        [('pricelist_id', '=', 5)],
        ['product_tmpl_id', 'fixed_price', 'compute_price']
    )
    usd_prices = {}
    for item in pricelist_items:
        tmpl = item.get('product_tmpl_id')
        if tmpl and isinstance(tmpl, (list, tuple)) and item.get('compute_price') == 'fixed':
            usd_prices[tmpl[0]] = float(item['fixed_price'])
    print(f"Encontrados {len(usd_prices)} productos con precio USD.")

    print("Buscando productos en Odoo...")
    products_data = odoo.env['product.template'].search_read([('active', '=', True)], fields)
    print(f"Encontrados {len(products_data)} productos. Procesando...")

    for p in products_data:
        raw_image = p.get('image_1920')
        image_bytes = base64.b64decode(raw_image) if raw_image else None

        raw_taxes = p.get('taxes_id') or []
        taxes_ids = [
            t[0] if isinstance(t, (list, tuple)) else t
            for t in raw_taxes
        ]

        usd_price = usd_prices.get(int(p['id']))
        product_data = {
            "odoo_id": int(p['id']),
            "name": str(p.get('name') or ""),
            "default_code": str(p.get('default_code') or ""),
            "barcode": str(p.get('barcode') or ""),
            "list_price": usd_price if usd_price is not None else float(p.get('list_price') or 0.0),
            "standard_price": float(p.get('standard_price') or 0.0),
            "type": str(p.get('type') or "product"),
            "categ_id": str(p.get('categ_id')[1] if p.get('categ_id') else ""),
            "uom_id": str(p.get('uom_id')[1] if p.get('uom_id') else ""),
            "description_sale": str(p.get('description_sale') or ""),
            "active": bool(p.get('active', True)),
            "sale_ok": bool(p.get('sale_ok', True)),
            "taxes_id": json.dumps(taxes_ids),
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
