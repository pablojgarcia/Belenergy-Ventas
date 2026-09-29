from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.integrations.odoo import sync as sync_module
from app.models import Product

TEST_DATABASE_URL = "sqlite:///./test.db"


def _session():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    return sessionmaker(bind=engine)()


def _fake_odoo(products_data):
    odoo = MagicMock()
    odoo.env["product.pricelist.item"].search_read.return_value = []
    odoo.env["product.category"].search_read.return_value = []
    odoo.env["product.template"].search_read.return_value = products_data
    return odoo


def _seed_products():
    """Producto 5 archivado en Odoo y 6 activo, ambos vendibles en la app."""
    db = _session()
    try:
        for odoo_id, stock in ((5, 25610.8), (6, 3.0)):
            db.add(Product(odoo_id=odoo_id, name=f"Producto {odoo_id}",
                           list_price=0.0, standard_price=0.0, type="product",
                           active=True, sale_ok=True, taxes_id="[]",
                           virtual_available=stock))
        db.commit()
    finally:
        db.close()


def _template_search_read_call(odoo):
    return odoo.env["product.template"].search_read.call_args


def test_sync_products_requests_virtual_available_directly(monkeypatch):
    products_data = [
        {"id": 1, "name": "Panel Solar", "default_code": "P1", "barcode": "1",
         "list_price": 100.0, "standard_price": 50.0, "type": "product",
         "categ_id": False, "uom_id": False, "description_sale": "",
         "active": True, "sale_ok": True, "image_1920": False,
         "taxes_id": [], "virtual_available": 7.5},
    ]
    odoo = _fake_odoo(products_data)
    monkeypatch.setattr(sync_module, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(sync_module.config.settings, "ODOO_WAREHOUSE_ID", None)

    db = _session()
    try:
        sync_module.sync_products(db)
    finally:
        db.close()

    args, kwargs = _template_search_read_call(odoo)
    fields = args[1]
    assert "virtual_available" in fields
    assert "qty_available" not in fields
    assert "incoming_qty" not in fields
    assert "outgoing_qty" not in fields

    db = _session()
    try:
        stored = db.query(Product).filter_by(odoo_id=1).first()
        assert stored.virtual_available == 7.5
    finally:
        db.close()


def test_sync_products_default_context_no_warehouse(monkeypatch):
    odoo = _fake_odoo([{"id": 1, "name": "P", "list_price": 1.0,
                        "standard_price": 1.0, "type": "product",
                        "categ_id": False, "uom_id": False, "active": True,
                        "sale_ok": True, "taxes_id": [], "virtual_available": 2.0}])
    monkeypatch.setattr(sync_module, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(sync_module.config.settings, "ODOO_WAREHOUSE_ID", None)

    db = _session()
    try:
        sync_module.sync_products(db)
    finally:
        db.close()

    _, kwargs = _template_search_read_call(odoo)
    assert "context" not in kwargs


def test_sync_products_forces_warehouse_context_when_configured(monkeypatch):
    odoo = _fake_odoo([{"id": 1, "name": "P", "list_price": 1.0,
                        "standard_price": 1.0, "type": "product",
                        "categ_id": False, "uom_id": False, "active": True,
                        "sale_ok": True, "taxes_id": [], "virtual_available": 2.0}])
    monkeypatch.setattr(sync_module, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(sync_module.config.settings, "ODOO_WAREHOUSE_ID", 7)

    db = _session()
    try:
        sync_module.sync_products(db)
    finally:
        db.close()

    _, kwargs = _template_search_read_call(odoo)
    assert kwargs.get("context") == {"warehouse_id": 7}


def test_sync_products_deactivates_products_archived_in_odoo(monkeypatch):
    """Un producto archivado en Odoo no debe quedar vendible en la app.

    El sync busca con `[('active', '=', True)]`, así que los archivados nunca
    entran en products_data y antes quedaban congelados con active=True y su
    stock viejo. El de odoo_id=5 es el caso real: 25.610 m de cable que en
    Odoo están en 0.
    """
    _seed_products()
    odoo = _fake_odoo([])
    odoo.env["product.template"].with_context.return_value.search.return_value = [5]
    monkeypatch.setattr(sync_module, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(sync_module.config.settings, "ODOO_WAREHOUSE_ID", None)

    db = _session()
    try:
        sync_module.sync_products(db)
    finally:
        db.close()

    db = _session()
    try:
        assert db.query(Product).filter_by(odoo_id=5).first().active is False
        # Los que Odoo sigue teniendo activos no se tocan.
        assert db.query(Product).filter_by(odoo_id=6).first().active is True
    finally:
        db.close()


def test_sync_products_archived_lookup_uses_active_test_false(monkeypatch):
    """Sin active_test=False la búsqueda de archivados no devuelve nada.

    active_test=True es justamente el filtro que esconde a los archivados, que
    es lo que estamos tratando de encontrar.
    """
    odoo = _fake_odoo([])
    monkeypatch.setattr(sync_module, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(sync_module.config.settings, "ODOO_WAREHOUSE_ID", None)

    db = _session()
    try:
        sync_module.sync_products(db)
    finally:
        db.close()

    odoo.env["product.template"].with_context.assert_any_call(active_test=False)
    domain = odoo.env["product.template"].with_context.return_value.search.call_args.args[0]
    assert ("active", "=", False) in domain


def test_products_endpoint_returns_virtual_available(client, admin_headers):
    db = _session()
    try:
        product = Product(odoo_id=99, name="Panel 575W", list_price=100.0,
                          standard_price=50.0, type="product", active=True,
                          sale_ok=True, taxes_id="[]", virtual_available=4.0)
        db.add(product)
        db.commit()
    finally:
        db.close()

    resp = client.get("/products", headers=admin_headers)
    assert resp.status_code == 200
    matches = [p for p in resp.json() if p["odoo_id"] == 99]
    assert matches
    assert matches[0]["virtual_available"] == 4.0
