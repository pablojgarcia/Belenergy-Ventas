from unittest.mock import patch

from app.integrations.odoo.partner import (
    create_partner,
    resolve_app_user_partner_id,
    resolve_res_users_id_by_name,
)


class _Users:
    def __init__(self, users):
        self.by_login = {}
        self.by_name = {}
        for u in users:
            self.by_login[u["login"]] = u
            self.by_name.setdefault(u["name"], u["id"])

    def search(self, domain):
        field, _, val = domain[0]
        if field == "login":
            u = self.by_login.get(val)
            return [u["id"]] if u else []
        return [self.by_name[val]] if val in self.by_name else []

    def read(self, ids, fields):
        if isinstance(ids, int):
            ids = [ids]
        out = []
        for uid in ids:
            for u in self.by_login.values():
                if u["id"] == uid:
                    row = {"id": uid}
                    for f in fields:
                        row[f] = u[f]
                    out.append(row)
        return out


class _Partners:
    def __init__(self, partners):
        self.by_email = {p["email"]: p["id"] for p in partners if p.get("email")}
        self.by_name = {}
        for p in partners:
            self.by_name.setdefault(p["name"], p["id"])

    def search(self, domain):
        field, _, val = domain[0]
        mapping = self.by_email if field == "email" else self.by_name
        return [mapping[val]] if val in mapping else []


class _FakeOdoo:
    def __init__(self, users, partners):
        self.env = {
            "res.users": _Users(users),
            "res.partner": _Partners(partners),
        }


def test_resolve_app_user_partner_id_via_user_login():
    fake = _FakeOdoo(
        users=[{"id": 1, "login": "vendedor@test.com", "name": "Vendedor", "partner_id": (10, "Vendedor")}],
        partners=[],
    )
    with patch("app.integrations.odoo.partner.get_odoo_connection", return_value=fake):
        assert resolve_app_user_partner_id("vendedor@test.com") == 10


def test_resolve_app_user_partner_id_fallback_to_partner_email():
    fake = _FakeOdoo(
        users=[],
        partners=[{"id": 20, "email": "vendedor@test.com", "name": "Vendedor"}],
    )
    with patch("app.integrations.odoo.partner.get_odoo_connection", return_value=fake):
        assert resolve_app_user_partner_id("vendedor@test.com") == 20


def test_resolve_app_user_partner_id_not_found():
    fake = _FakeOdoo(users=[], partners=[])
    with patch("app.integrations.odoo.partner.get_odoo_connection", return_value=fake):
        assert resolve_app_user_partner_id("nadie@test.com") is None
        assert resolve_app_user_partner_id(None) is None


def test_resolve_res_users_id_by_name():
    fake = _FakeOdoo(
        users=[{"id": 30, "login": "a@test.com", "name": "Carlos Interno", "partner_id": False}],
        partners=[],
    )
    with patch("app.integrations.odoo.partner.get_odoo_connection", return_value=fake):
        assert resolve_res_users_id_by_name("Carlos Interno") == 30
        assert resolve_res_users_id_by_name("Inexistente") is None
        assert resolve_res_users_id_by_name("") is None
        assert resolve_res_users_id_by_name(None) is None


class _CreatingOdoo:
    def __init__(self):
        self.env = {
            "res.partner": self,
            "res.users": self,
            "res.country.state": self,
            "res.country": self,
        }
        self.created_vals = None

    def search_count(self, domain):
        return 0

    def search(self, domain):
        return []

    def read(self, ids, fields):
        return [{"partner_id": [1]}]

    def create(self, vals):
        self.created_vals = vals
        return 100001


def test_create_partner_empresa():
    fake = _CreatingOdoo()
    with patch("app.integrations.odoo.partner.get_odoo_connection", return_value=fake):
        create_partner({
            "company_name": "Empresa SA",
            "contact_name": "Empresa SA",
            "vat": "30600000000",
            "is_company": True,
        })
    assert fake.created_vals["company_type"] == "company"
    assert fake.created_vals["name"] == "Empresa SA"
    assert fake.created_vals["company_name"] == "Empresa SA"
    assert "industry_id" not in fake.created_vals


def test_create_partner_persona():
    fake = _CreatingOdoo()
    with patch("app.integrations.odoo.partner.get_odoo_connection", return_value=fake):
        create_partner({
            "company_name": "Persona",
            "contact_name": "Juan Pérez",
            "vat": "30600000000",
            "is_company": False,
        })
    assert fake.created_vals["company_type"] == "person"
    assert fake.created_vals["name"] == "Juan Pérez"
    assert fake.created_vals["company_name"] == ""


def test_create_partner_includes_industry_id():
    fake = _CreatingOdoo()
    with patch("app.integrations.odoo.partner.get_odoo_connection", return_value=fake):
        create_partner({
            "company_name": "Campo SA",
            "contact_name": "Campo SA",
            "vat": "30600000000",
            "industry_id": 42,
        })
    assert fake.created_vals["industry_id"] == 42
