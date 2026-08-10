from unittest.mock import patch

from app.integrations.odoo.partner import (
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
