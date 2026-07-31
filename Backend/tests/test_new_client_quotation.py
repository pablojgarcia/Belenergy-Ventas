import uuid
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base

TEST_DATABASE_URL = "sqlite:///./test.db"


def _seed_product():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    product = models.Product(
        name="Panel Solar 500W",
        odoo_id=999001,
        default_code="PANEL-500",
        list_price=1000.0,
    )
    db.add(product)
    db.commit()
    pid = product.id
    db.close()
    return pid


class _FakeOdoo:
    def __init__(self):
        self.env = {
            "res.partner": self,
            "product.product": self,
            "sale.order": self,
        }

    def search_count(self, domain):
        return 1

    def create(self, vals):
        return 888888

    def read(self, ids, fields):
        if isinstance(ids, int):
            return [{"name": f"SO{ids}"}]
        return [{"name": f"SO{i}"} for i in ids]


def test_draft_with_new_client_keeps_customer_id_null(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Nuevo Test SRL",
            "new_client_vat": "30600000000",
            "notes": "Prueba cliente nuevo",
            "lines": [
                {"product_id": 1, "quantity": 2, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["customer_id"] is None
    assert body["new_client_name"] == "Cliente Nuevo Test SRL"
    assert body["new_client_vat"] == "30600000000"


def test_generate_creates_customer_then_quotation(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Generado SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    draft_id = resp.json()["id"]

    with patch(
        "app.services.customer_creation_service.odoo_create_partner",
        return_value=777777,
    ), patch(
        "app.services.customer_creation_service.check_vat_exists",
        return_value=False,
    ), patch(
        "app.integrations.odoo.sale.create_quotation",
        return_value=888888,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection",
        return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection",
        return_value=_FakeOdoo(),
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    assert gen.status_code == 200, gen.text
    gen_body = gen.json()
    assert gen_body["odoo_sale_order_id"] == 888888
    assert gen_body["odoo_sale_order_name"] == "SO888888"

    draft = client.get(f"/quotation-drafts/{draft_id}", headers=admin_headers).json()
    assert draft["customer_id"] is not None
    assert draft["new_client_name"] is None
    assert draft["new_client_vat"] is None
    assert draft["status"] == "generated"

    customers = client.get("/customers", headers=admin_headers).json()
    created = next(c for c in customers if c["odoo_id"] == 777777)
    assert created["name"] == "Cliente Generado SRL"
    assert created["cuit"] == "30600000000"


def test_generate_with_invalid_cuit_fails(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente CUIT Malo",
            "new_client_vat": "30600000001",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    draft_id = resp.json()["id"]

    with patch(
        "app.services.customer_creation_service.odoo_create_partner"
    ) as create_partner, patch(
        "app.services.customer_creation_service.check_vat_exists"
    ) as check_vat:
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    assert gen.status_code == 400
    create_partner.assert_not_called()
    check_vat.assert_not_called()

    draft = client.get(f"/quotation-drafts/{draft_id}", headers=admin_headers).json()
    assert draft["status"] == "failed"


def test_generate_without_client_fails(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    draft_id = resp.json()["id"]

    gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)
    assert gen.status_code == 400
