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


def test_generate_with_duplicate_cuit_returns_structured_409(client, admin_headers):
    _seed_product()

    def _make_draft(name):
        resp = client.post(
            "/quotation-drafts",
            headers=admin_headers,
            json={
                "new_client_name": name,
                "new_client_vat": "30600000000",
                "lines": [
                    {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
                ],
            },
        )
        assert resp.status_code == 201, resp.text
        return resp.json()["id"]

    draft1 = _make_draft("Cliente Original SRL")
    with patch(
        "app.services.customer_creation_service.odoo_create_partner", return_value=777777,
    ), patch(
        "app.services.customer_creation_service.check_vat_exists", return_value=False,
    ), patch(
        "app.integrations.odoo.sale.create_quotation", return_value=888888,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection", return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=_FakeOdoo(),
    ):
        gen1 = client.post(f"/quotation-drafts/{draft1}/generate", headers=admin_headers)
    assert gen1.status_code == 200, gen1.text

    draft2 = _make_draft("Cliente Duplicado SRL")
    gen2 = client.post(f"/quotation-drafts/{draft2}/generate", headers=admin_headers)
    assert gen2.status_code == 409
    body = gen2.json()
    assert body["title"] == "Cliente duplicado"
    assert "Ya existe un cliente con ese CUIT" in body["detail"]


def test_generate_without_cuit_fails_and_draft_marks_failed(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Sin CUIT SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    draft_id = resp.json()["id"]

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    draft = db.query(models.QuotationDraft).filter(models.QuotationDraft.id == uuid.UUID(draft_id)).first()
    draft.new_client_vat = None
    db.commit()
    db.close()

    gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)
    assert gen.status_code == 400
    body = gen.json()
    assert body["title"] == "Solicitud inválida"
    assert "CUIT es obligatorio" in body["detail"]

    draft = client.get(f"/quotation-drafts/{draft_id}", headers=admin_headers).json()
    assert draft["status"] == "failed"


def test_draft_new_client_requires_cuit_on_create(client, admin_headers):
    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Sin CUIT SRL",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    assert resp.status_code == 400
    assert "CUIT es obligatorio" in resp.json()["detail"]


def test_update_failed_draft_allowed(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Fallido SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    draft_id = resp.json()["id"]

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    draft = db.query(models.QuotationDraft).filter(models.QuotationDraft.id == uuid.UUID(draft_id)).first()
    draft.status = "failed"
    db.commit()
    db.close()

    upd = client.put(
        f"/quotation-drafts/{draft_id}",
        headers=admin_headers,
        json={
            "version": 1,
            "new_client_name": "Cliente Fallido Editado SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 2, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    assert upd.status_code == 200, upd.text
    assert upd.json()["status"] == "failed"


def test_generate_sets_quotation_status_draft(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Status SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    draft_id = resp.json()["id"]

    with patch(
        "app.services.customer_creation_service.odoo_create_partner", return_value=777777,
    ), patch(
        "app.services.customer_creation_service.check_vat_exists", return_value=False,
    ), patch(
        "app.integrations.odoo.sale.create_quotation", return_value=888888,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection", return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=_FakeOdoo(),
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)
    assert gen.status_code == 200, gen.text

    quotation = client.get(f"/quotations/{draft_id}", headers=admin_headers).json()
    assert quotation["status"] == "draft"


def test_refresh_status_updates_quotation_from_odoo(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Refresh SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    draft_id = resp.json()["id"]

    with patch(
        "app.services.customer_creation_service.odoo_create_partner", return_value=777777,
    ), patch(
        "app.services.customer_creation_service.check_vat_exists", return_value=False,
    ), patch(
        "app.integrations.odoo.sale.create_quotation", return_value=888888,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection", return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=_FakeOdoo(),
    ):
        client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    with patch(
        "app.services.quotation_query_service.get_quotation_state", return_value="sale",
    ):
        refresh = client.post(f"/quotations/{draft_id}/refresh-status", headers=admin_headers)
    assert refresh.status_code == 200, refresh.text
    assert refresh.json()["status"] == "sale"

    quotation = client.get(f"/quotations/{draft_id}", headers=admin_headers).json()
    assert quotation["status"] == "sale"


def test_generated_draft_not_in_drafts_list(client, admin_headers):
    _seed_product()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Listado SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
    )
    draft_id = resp.json()["id"]

    with patch(
        "app.services.customer_creation_service.odoo_create_partner", return_value=777777,
    ), patch(
        "app.services.customer_creation_service.check_vat_exists", return_value=False,
    ), patch(
        "app.integrations.odoo.sale.create_quotation", return_value=888888,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection", return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=_FakeOdoo(),
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)
    assert gen.status_code == 200, gen.text

    drafts = client.get("/quotation-drafts", headers=admin_headers).json()
    assert all(d["id"] != draft_id for d in drafts), "Borrador generado no debería listarse"

    quotations = client.get("/quotations", headers=admin_headers).json()
    assert any(q["id"] == draft_id for q in quotations), "La cotización generada debería listarse"
