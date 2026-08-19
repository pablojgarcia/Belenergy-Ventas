from unittest.mock import MagicMock

from app.integrations.odoo import industry as industry_module
from app.integrations.odoo.industry import (
    SELLER_TYPE_TO_INDUSTRY,
    auto_industry_for_seller_types,
    clear_industry_cache,
    effective_seller_type,
    industry_to_seller_type,
    mapped_industries,
    principal_seller_type,
    resolve_industry_id,
    user_seller_types,
)


def test_user_seller_types_prefers_list():
    assert user_seller_types(["representante_agro", "representante_general"]) == [
        "representante_agro",
        "representante_general",
    ]


def test_user_seller_types_ignores_empty_list():
    assert user_seller_types([]) == ["representante_general"]


def test_user_seller_types_default_internal():
    assert user_seller_types(None) == ["representante_general"]


def test_principal_seller_type_first_element():
    assert principal_seller_type(["representante_general", "representante_agro"]) == "representante_general"


def test_principal_seller_type_default_internal():
    assert principal_seller_type(None) == "representante_general"
    assert principal_seller_type([]) == "representante_general"


def test_mapped_industries_single():
    result = mapped_industries(["representante_agro"])
    assert result == [{"name": "Agricultura", "seller_type": "representante_agro"}]


def test_mapped_industries_multi_no_duplicates():
    result = mapped_industries(["representante_agro", "representante_agro", "representante_general"])
    assert result == [{"name": "Agricultura", "seller_type": "representante_agro"}]


def test_mapped_industries_empty_for_unmapped():
    assert mapped_industries(["representante_general"]) == []


def test_auto_industry_single_seller_type():
    assert auto_industry_for_seller_types(["representante_agro"]) == "Agricultura"


def test_auto_industry_none_for_multi():
    assert auto_industry_for_seller_types(["representante_agro", "representante_general"]) is None


def test_auto_industry_none_for_unmapped():
    assert auto_industry_for_seller_types(["representante_general"]) is None


def test_industry_to_seller_type_roundtrip():
    assert industry_to_seller_type("Agricultura") == "representante_agro"
    assert industry_to_seller_type("Inexistente") is None
    assert industry_to_seller_type(None) is None


def test_effective_seller_type_with_industry():
    assert (
        effective_seller_type(["representante_general", "representante_agro"], "Agricultura")
        == "representante_agro"
    )


def test_effective_seller_type_without_industry_uses_principal():
    assert (
        effective_seller_type(["representante_general", "representante_agro"], None)
        == "representante_general"
    )


def test_effective_seller_type_fallback_internal():
    assert effective_seller_type([], None) == "representante_general"


def test_mapping_has_known_seller_type():
    assert "representante_agro" in SELLER_TYPE_TO_INDUSTRY


def test_resolve_industry_id_hits_odoo(monkeypatch):
    clear_industry_cache()
    fake_odoo = MagicMock()
    fake_odoo.env["res.partner.industry"].search.return_value = [42]
    monkeypatch.setattr(industry_module, "get_odoo_connection", lambda: fake_odoo)

    assert resolve_industry_id("Agricultura") == 42
    fake_odoo.env["res.partner.industry"].search.assert_called_once_with(
        [("name", "=", "Agricultura")]
    )


def test_resolve_industry_id_cached(monkeypatch):
    clear_industry_cache()
    fake_odoo = MagicMock()
    fake_odoo.env["res.partner.industry"].search.return_value = [7]
    monkeypatch.setattr(industry_module, "get_odoo_connection", lambda: fake_odoo)

    resolve_industry_id("Agricultura")
    fake_odoo.env["res.partner.industry"].search.reset_mock()
    assert resolve_industry_id("Agricultura") == 7
    fake_odoo.env["res.partner.industry"].search.assert_not_called()


def test_resolve_industry_id_not_found(monkeypatch):
    clear_industry_cache()
    fake_odoo = MagicMock()
    fake_odoo.env["res.partner.industry"].search.return_value = []
    monkeypatch.setattr(industry_module, "get_odoo_connection", lambda: fake_odoo)

    assert resolve_industry_id("Inexistente") is None


def test_resolve_industry_id_fallback_to_old_model(monkeypatch):
    clear_industry_cache()

    class _Env:
        def __getitem__(self, name):
            if name == "res.partner.industry":
                raise RuntimeError("model res.partner.industry doesn't exist")
            return MagicMock(search=MagicMock(return_value=[9]))

    fake_odoo = MagicMock()
    fake_odoo.env = _Env()
    monkeypatch.setattr(industry_module, "get_odoo_connection", lambda: fake_odoo)

    assert resolve_industry_id("Agricultura") == 9


def test_resolve_industry_id_connection_error(monkeypatch):
    clear_industry_cache()
    monkeypatch.setattr(
        industry_module,
        "get_odoo_connection",
        lambda: (_ for _ in ()).throw(RuntimeError("no odoo")),
    )
    assert resolve_industry_id("Agricultura") is None


def test_resolve_industry_id_none():
    assert resolve_industry_id(None) is None
