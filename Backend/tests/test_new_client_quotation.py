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

    line = db.query(models.ProductLine).filter(models.ProductLine.key == "test_line").first()
    if not line:
        line = models.ProductLine(key="test_line", name="Línea de Test", is_active=True)
        db.add(line)
        db.commit()
        db.refresh(line)

    for seller_type in ("representante_general", "representante_agro"):
        rule = db.query(models.DiscountRule).filter(
            models.DiscountRule.seller_type == seller_type,
            models.DiscountRule.product_line_id == line.id,
        ).first()
        if not rule:
            db.add(models.DiscountRule(
                seller_type=seller_type,
                product_line_id=line.id,
                condition_type="amount",
                min_value=0.0,
                max_value=None,
                max_discount=0.0,
                requires_approval=False,
                is_active=True,
            ))
    db.commit()

    product = models.Product(
        name="Panel Solar 500W",
        odoo_id=999001,
        default_code="PANEL-500",
        list_price=1000.0,
        product_line_id=line.id,
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
        self.last_created_vals = None

    def search_count(self, domain):
        return 1

    def search_read(self, domain, fields, limit=None):
        for field, op, value in domain:
            if field == "id" and op == "=":
                rows = [{"id": value}]
                break
            if field == "id" and op == "in":
                rows = [{"id": i} for i in value]
                break
        else:
            rows = [{"id": 1}]
        return rows[:limit] if limit else rows

    def create(self, vals):
        self.last_created_vals = vals
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
            "new_client_industry": "Agricultura",
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
        "app.services.customer_creation_service.resolve_industry_id",
        return_value=1,
    ), patch(
        "app.integrations.odoo.sale.create_quotation",
        return_value=888888,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection",
        return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection",
        return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id",
        return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name",
        return_value=None,
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
    assert created["industry"] == "Agricultura"


def test_generate_sets_vendedor_externo_and_vendedor_interno(client, admin_headers):
    _seed_product()
    fake = _FakeOdoo()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Vendedores SRL",
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
        "app.integrations.odoo.sale.get_odoo_connection", return_value=fake,
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=fake,
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=555555,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=444444,
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    assert gen.status_code == 200, gen.text
    assert fake.last_created_vals is not None
    assert fake.last_created_vals["user_id"] == 444444
    assert fake.last_created_vals["x_studio_vendedor_externo"] == 555555


def test_generate_skips_vendedores_when_not_resolvable(client, admin_headers):
    _seed_product()
    fake = _FakeOdoo()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Sin Vendedores SRL",
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
        "app.integrations.odoo.sale.get_odoo_connection", return_value=fake,
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=fake,
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=None,
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    assert gen.status_code == 200, gen.text
    assert fake.last_created_vals is not None
    assert "user_id" not in fake.last_created_vals
    assert "x_studio_vendedor_externo" not in fake.last_created_vals


def test_create_quotation_always_sends_approval_fields(client):
    from app.integrations.odoo.sale import create_quotation
    fake = _FakeOdoo()
    with patch("app.integrations.odoo.sale.get_odoo_connection", return_value=fake):
        create_quotation(
            partner_id=1,
            order_lines=[{"product_id": 1, "quantity": 1, "price_unit": 1000.0}],
            description="Nota",
            requiere_aprobacion=False,
            motivo_aprobacion="",
        )
    assert fake.last_created_vals is not None
    assert fake.last_created_vals["x_studio_requiere_aprobacion"] is False
    assert fake.last_created_vals["x_studio_motivo_aprobacion_1"] == ""


def test_create_quotation_sends_approval_fields_when_exceeded(client):
    from app.integrations.odoo.sale import create_quotation
    fake = _FakeOdoo()
    with patch("app.integrations.odoo.sale.get_odoo_connection", return_value=fake):
        create_quotation(
            partner_id=1,
            order_lines=[{"product_id": 1, "quantity": 1, "price_unit": 1000.0}],
            description="Nota",
            requiere_aprobacion=True,
            motivo_aprobacion="El descuento de la línea #1 supera el máximo.",
        )
    assert fake.last_created_vals is not None
    assert fake.last_created_vals["x_studio_requiere_aprobacion"] is True
    assert fake.last_created_vals["x_studio_motivo_aprobacion_1"] == "El descuento de la línea #1 supera el máximo."


def test_generate_does_not_block_on_exceeded_discount(client, admin_headers):
    _seed_product()
    fake = _FakeOdoo()

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()

    line = models.ProductLine(key="deye", name="Línea DEYE", is_active=True)
    db.add(line)
    db.commit()
    db.refresh(line)

    product = db.query(models.Product).filter(models.Product.odoo_id == 999001).first()
    product.product_line_id = line.id
    db.commit()

    db.add(models.DiscountRule(
        seller_type="representante_general",
        product_line_id=line.id,
        condition_type="amount",
        min_value=500.0,
        max_value=5000.0,
        max_discount=5.0,
        requires_approval=False,
        is_active=True,
    ))
    db.commit()
    db.close()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Excede Descuento SRL",
            "new_client_vat": "30600000000",
            "notes": "Descuento especial aprobado por gerencia",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "discount": 34.0, "tax_id": []}
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    draft_id = resp.json()["id"]

    with patch(
        "app.services.customer_creation_service.odoo_create_partner", return_value=777777,
    ), patch(
        "app.services.customer_creation_service.check_vat_exists", return_value=False,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection", return_value=fake,
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=fake,
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=None,
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    assert gen.status_code == 200, gen.text
    assert fake.last_created_vals is not None
    assert fake.last_created_vals["x_studio_requiere_aprobacion"] is True
    assert fake.last_created_vals["x_studio_motivo_aprobacion_1"] == "Descuento especial aprobado por gerencia"


def test_generate_blocks_when_exceeded_without_description(client, admin_headers):
    _seed_product()

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()

    line = models.ProductLine(key="deye", name="Línea DEYE", is_active=True)
    db.add(line)
    db.commit()
    db.refresh(line)

    product = db.query(models.Product).filter(models.Product.odoo_id == 999001).first()
    product.product_line_id = line.id
    db.commit()

    db.add(models.DiscountRule(
        seller_type="representante_general",
        product_line_id=line.id,
        condition_type="amount",
        min_value=500.0,
        max_value=5000.0,
        max_discount=5.0,
        requires_approval=False,
        is_active=True,
    ))
    db.commit()
    db.close()

    resp = client.post(
        "/quotation-drafts",
        headers=admin_headers,
        json={
            "new_client_name": "Cliente Excede Sin Desc SRL",
            "new_client_vat": "30600000000",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "discount": 34.0, "tax_id": []}
            ],
        },
    )
    assert resp.status_code == 201, resp.text
    draft_id = resp.json()["id"]

    with patch(
        "app.services.customer_creation_service.odoo_create_partner", return_value=777777,
    ), patch(
        "app.services.customer_creation_service.check_vat_exists", return_value=False,
    ), patch(
        "app.integrations.odoo.sale.get_odoo_connection", return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.get_odoo_connection", return_value=_FakeOdoo(),
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=None,
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    assert gen.status_code == 400
    body = gen.json()
    assert body["title"] == "Solicitud inválida"
    assert "descripción es obligatoria" in body["detail"].lower()


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
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=None,
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
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=None,
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
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=None,
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
    ), patch(
        "app.services.quotation_generation_service.resolve_app_user_partner_id", return_value=None,
    ), patch(
        "app.services.quotation_generation_service.resolve_res_users_id_by_name", return_value=None,
    ):
        gen = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)
    assert gen.status_code == 200, gen.text

    drafts = client.get("/quotation-drafts", headers=admin_headers).json()
    assert all(d["id"] != draft_id for d in drafts), "Borrador generado no debería listarse"

    quotations = client.get("/quotations", headers=admin_headers).json()
    assert any(q["id"] == draft_id for q in quotations), "La cotización generada debería listarse"


def _seed_customers():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    agro = models.Customer(odoo_id=500001, name="Campo SRL", industry="Agricultura")
    otro = models.Customer(odoo_id=500002, name="Otra SA", industry="Tecnología")
    sin = models.Customer(odoo_id=500003, name="Sin Industria SA")
    db.add_all([agro, otro, sin])
    db.commit()
    db.close()


def test_customers_list_includes_industry(client, admin_headers):
    _seed_customers()
    customers = client.get("/customers", headers=admin_headers).json()
    by_name = {c["name"]: c for c in customers}
    assert by_name["Campo SRL"]["industry"] == "Agricultura"
    assert by_name["Otra SA"]["industry"] == "Tecnología"
    assert by_name["Sin Industria SA"]["industry"] is None


def test_customers_industry_filter(client, admin_headers):
    _seed_customers()
    agro = client.get("/customers", headers=admin_headers, params={"industry": "Agricultura"}).json()
    names = {c["name"] for c in agro}
    assert names == {"Campo SRL"}

    tech = client.get("/customers", headers=admin_headers, params={"industry": "Tecnología"}).json()
    assert {c["name"] for c in tech} == {"Otra SA"}

    missing = client.get("/customers", headers=admin_headers, params={"industry": "Inexistente"}).json()
    assert missing == []


def test_customers_industry_filter_scoped_to_salesperson(client, admin_headers):
    resp = client.post(
        "/auth/register",
        headers=admin_headers,
        json={
            "username": "vendagro",
            "email": "vendagro@test.com",
            "name": "Vendedor Agro",
            "role": "vendedor",
            "password": "pass123",
            "seller_types": ["representante_general", "representante_agro"],
        },
    )
    assert resp.status_code == 201, resp.text
    login = client.post("/auth/login", json={"username": "vendagro", "password": "pass123"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Session = sessionmaker(bind=engine)
    db = Session()
    db.add_all([
        models.Customer(odoo_id=600001, name="Mio Agro SA", salesperson_id="vendagro@test.com", industry="Agricultura"),
        models.Customer(odoo_id=600002, name="Mio Tech SA", salesperson_id="vendagro@test.com", industry="Tecnología"),
        models.Customer(odoo_id=600003, name="De Otro Agro SA", salesperson_id="otro@test.com", industry="Agricultura"),
    ])
    db.commit()
    db.close()

    mine = client.get("/customers", headers=headers, params={"industry": "Agricultura"}).json()
    assert {c["name"] for c in mine} == {"Mio Agro SA"}

    all_mine = client.get("/customers", headers=headers).json()
    assert {c["name"] for c in all_mine} == {"Mio Agro SA", "Mio Tech SA"}
