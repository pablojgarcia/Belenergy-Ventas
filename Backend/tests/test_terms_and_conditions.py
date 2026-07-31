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


def _make_user_token():
    token = create_access_token(
        {"username": "vendedor", "type": "access"},
        expires_delta=timedelta(hours=1),
    )
    return {"Authorization": f"Bearer {token}"}


def test_list_terms_empty(admin_headers, client):
    resp = client.get("/terms-and-conditions", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json() == []


def test_create_terms(admin_headers, client):
    resp = client.post(
        "/terms-and-conditions",
        json={"name": "T&C Test", "content": "Contenido de prueba", "is_default": False},
        headers=admin_headers,
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "T&C Test"
    assert data["content"] == "Contenido de prueba"
    assert data["is_default"] is False
    assert data["is_active"] is True
    assert "id" in data


def test_get_terms(admin_headers, client):
    create_resp = client.post(
        "/terms-and-conditions",
        json={"name": "T&C Obtener", "content": "Contenido"},
        headers=admin_headers,
    )
    terms_id = create_resp.json()["id"]

    resp = client.get(f"/terms-and-conditions/{terms_id}", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "T&C Obtener"


def test_get_terms_not_found(admin_headers, client):
    resp = client.get(
        f"/terms-and-conditions/{uuid.uuid4()}", headers=admin_headers
    )
    assert resp.status_code == 404


def test_update_terms(admin_headers, client):
    create_resp = client.post(
        "/terms-and-conditions",
        json={"name": "T&C Original", "content": "Original"},
        headers=admin_headers,
    )
    terms_id = create_resp.json()["id"]

    resp = client.put(
        f"/terms-and-conditions/{terms_id}",
        json={"name": "T&C Actualizado", "content": "Actualizado"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "T&C Actualizado"
    assert resp.json()["content"] == "Actualizado"


def test_delete_terms(admin_headers, client):
    create_resp = client.post(
        "/terms-and-conditions",
        json={"name": "T&C Eliminar", "content": "Eliminar"},
        headers=admin_headers,
    )
    terms_id = create_resp.json()["id"]

    resp = client.delete(f"/terms-and-conditions/{terms_id}", headers=admin_headers)
    assert resp.status_code == 204

    get_resp = client.get(f"/terms-and-conditions/{terms_id}", headers=admin_headers)
    assert get_resp.status_code == 404


def test_list_terms_active_only(admin_headers, client):
    client.post(
        "/terms-and-conditions",
        json={"name": "T&C Activo", "content": "Activo"},
        headers=admin_headers,
    )
    client.post(
        "/terms-and-conditions",
        json={"name": "T&C Inactivo", "content": "Inactivo"},
        headers=admin_headers,
    )

    resp = client.get("/terms-and-conditions", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_create_draft_with_terms(admin_headers, client):
    terms_resp = client.post(
        "/terms-and-conditions",
        json={"name": "T&C Draft", "content": "Contenido T&C"},
        headers=admin_headers,
    )
    terms_id = terms_resp.json()["id"]

    resp = client.post(
        "/quotation-drafts",
        json={
            "new_client_name": "Cliente Nuevo T&C",
            "new_client_vat": "30600000000",
            "terms_and_conditions_id": terms_id,
            "notes": "Nota de prueba",
            "lines": [],
        },
        headers=admin_headers,
    )
    assert resp.status_code == 201
    assert resp.json()["terms_and_conditions_id"] == terms_id


def test_generate_quotation_uses_terms_note(admin_headers, client):
    _seed_product()

    terms_resp = client.post(
        "/terms-and-conditions",
        json={"name": "T&C Generacion", "content": "Términos de generación"},
        headers=admin_headers,
    )
    terms_id = terms_resp.json()["id"]

    draft_resp = client.post(
        "/quotation-drafts",
        json={
            "new_client_name": "Cliente T&C Generado",
            "new_client_vat": "30600000000",
            "terms_and_conditions_id": terms_id,
            "notes": "Nota interna",
            "lines": [
                {"product_id": 1, "quantity": 1, "unit_price": 1000.0, "tax_id": []}
            ],
        },
        headers=admin_headers,
    )
    draft_id = draft_resp.json()["id"]

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
        resp = client.post(f"/quotation-drafts/{draft_id}/generate", headers=admin_headers)

    assert resp.status_code == 200
    assert resp.json()["odoo_sale_order_name"] is not None