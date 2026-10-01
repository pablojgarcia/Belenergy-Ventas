from datetime import datetime, timezone
from unittest.mock import MagicMock

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.integrations.odoo import sync as m
from app.models import SyncRun


def _session():
    engine = create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
    return sessionmaker(bind=engine)()


class _FakeEnv:
    def __init__(self):
        self._mocks = {}

    def __getitem__(self, key):
        if key not in self._mocks:
            self._mocks[key] = MagicMock()
        return self._mocks[key]


def _fake_odoo():
    odoo = MagicMock()
    odoo.env = _FakeEnv()
    return odoo


def test_delta_cutoff_offsets_by_two_minutes_and_truncates_micros():
    last = datetime(2026, 9, 7, 3, 0, 5, 123456, tzinfo=timezone.utc)
    assert m._delta_cutoff(last) == "2026-09-07 02:58:05"
    assert m._delta_cutoff(None) is None


def test_sync_customers_full_scan_first_run(monkeypatch):
    odoo = _fake_odoo()
    odoo.env["res.partner"].search_read.return_value = []
    monkeypatch.setattr(m, "get_odoo_connection", lambda: odoo)
    db = _session()
    try:
        m.sync_customers(db)
    finally:
        db.close()
    domain = odoo.env["res.partner"].search_read.call_args_list[0].args[0]
    assert domain == []


def test_sync_customers_delta_domain_from_last_run(monkeypatch):
    odoo = _fake_odoo()
    odoo.env["res.partner"].search_read.return_value = []
    monkeypatch.setattr(m, "get_odoo_connection", lambda: odoo)
    db = _session()
    try:
        db.add(SyncRun(sync_type="customers", status="completed",
                       finished_at=datetime(2026, 9, 7, 3, 0, tzinfo=timezone.utc)))
        db.commit()
        m.sync_customers(db)
    finally:
        db.close()
    domain = odoo.env["res.partner"].search_read.call_args_list[0].args[0]
    assert domain == [("write_date", ">", "2026-09-07 02:58:00")]


def test_sync_products_delta_merges_write_date_and_recent_stock(monkeypatch):
    odoo = _fake_odoo()
    odoo.env["product.pricelist.item"].search_read.return_value = []
    odoo.env["product.category"].search_read.return_value = []
    odoo.env["product.template"].search.return_value = [11, 22]
    # El modelo es `stock.move`, no `product.stock.move`, y la búsqueda va con
    # with_context(active_test=False).
    odoo.env["stock.move"].with_context.return_value.search_read.return_value = [{"product_id": [33]}]
    odoo.env["product.product"].read.return_value = [{"id": 33, "product_tmpl_id": [44]}]
    odoo.env["product.template"].search_read.return_value = []
    monkeypatch.setattr(m, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(m.config.settings, "ODOO_WAREHOUSE_ID", None)
    db = _session()
    try:
        db.add(SyncRun(sync_type="products", status="completed",
                       finished_at=datetime(2026, 9, 7, 3, 0, tzinfo=timezone.utc)))
        db.commit()
        m.sync_products(db)
    finally:
        db.close()
    domain = odoo.env["product.template"].search_read.call_args_list[-1].args[0]
    assert domain[0][0] == "id"
    assert sorted(domain[0][2]) == [11, 22, 44]


def test_sync_products_stock_delta_filters_by_write_date_not_date(monkeypatch):
    """El corte del delta de stock debe ser `write_date`.

    Con `date` (fecha programada) se perdían para siempre las recepciones cargadas
    con fecha anterior, las cancelaciones y los cambios de cantidad: `since` solo
    crece y nunca vuelve a alcanzar esos movimientos.
    """
    odoo = _fake_odoo()
    odoo.env["product.pricelist.item"].search_read.return_value = []
    odoo.env["product.category"].search_read.return_value = []
    odoo.env["product.template"].search.return_value = []
    moves = odoo.env["stock.move"].with_context.return_value
    moves.search_read.return_value = []
    odoo.env["product.template"].search_read.return_value = []
    monkeypatch.setattr(m, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(m.config.settings, "ODOO_WAREHOUSE_ID", None)
    db = _session()
    try:
        db.add(SyncRun(sync_type="products", status="completed",
                       finished_at=datetime(2026, 9, 7, 3, 0, tzinfo=timezone.utc)))
        db.commit()
        m.sync_products(db)
    finally:
        db.close()
    odoo.env["stock.move"].with_context.assert_called_once_with(active_test=False)
    assert moves.search_read.call_args.args[0] == [("write_date", ">=", "2026-09-07 02:58:00")]


def test_sync_products_never_queries_nonexistent_product_stock_move_model(monkeypatch):
    """`product.stock.move` no existe en Odoo: la consulta reventaba siempre."""
    odoo = _fake_odoo()
    odoo.env["product.pricelist.item"].search_read.return_value = []
    odoo.env["product.category"].search_read.return_value = []
    odoo.env["product.template"].search.return_value = []
    odoo.env["stock.move"].with_context.return_value.search_read.return_value = []
    odoo.env["product.template"].search_read.return_value = []
    monkeypatch.setattr(m, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(m.config.settings, "ODOO_WAREHOUSE_ID", None)
    db = _session()
    try:
        db.add(SyncRun(sync_type="products", status="completed",
                       finished_at=datetime(2026, 9, 7, 3, 0, tzinfo=timezone.utc)))
        db.commit()
        m.sync_products(db)
    finally:
        db.close()
    assert "product.stock.move" not in odoo.env._mocks


def test_sync_products_force_full_ignores_delta(monkeypatch):
    """force_full=True no debe calcular ni usar el corte por write_date."""
    odoo = _fake_odoo()
    odoo.env["product.pricelist.item"].search_read.return_value = []
    odoo.env["product.category"].search_read.return_value = []
    # No hay cambios por write_date, pero force_full debe ignorarlo
    odoo.env["product.template"].search.return_value = []
    odoo.env["stock.move"].with_context.return_value.search_read.return_value = []
    # El camino full pide TODOS los productos activos
    odoo.env["product.template"].search_read.return_value = [
        {
            "id": 7,
            "name": "P",
            "list_price": 1.0,
            "standard_price": 1.0,
            "type": "product",
            "categ_id": False,
            "uom_id": False,
            "description_sale": "",
            "active": True,
            "sale_ok": True,
            "taxes_id": [],
            "image_1920": False,
            "virtual_available": 5.0,
        }
    ]
    monkeypatch.setattr(m, "get_odoo_connection", lambda: odoo)
    monkeypatch.setattr(m.config.settings, "ODOO_WAREHOUSE_ID", None)
    db = _session()
    try:
        db.add(SyncRun(sync_type="products", status="completed",
                       finished_at=datetime(2026, 9, 7, 3, 0, tzinfo=timezone.utc)))
        db.commit()
        m.sync_products(db, force_full=True)
    finally:
        db.close()
    # En full, NO llama a stock.move en el cálculo del delta
    assert odoo.env["stock.move"].with_context.call_count == 0
    # La búsqueda full es por active=True
    domain = odoo.env["product.template"].search_read.call_args.args[0]
    assert domain == [("active", "=", True)]