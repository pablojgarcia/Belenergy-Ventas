from app.integrations.odoo.sync import _resolve_product_line, _normalize_name


def _cat_map():
    return {
        1: {"name": "Goods", "parent_id": None},
        6: {"name": "Inversores", "parent_id": 1},
        7: {"name": "Paneles Fotovoltaicos", "parent_id": 1},
        8: {"name": "Cableado", "parent_id": 1},
        9: {"name": "ACCESORIOS", "parent_id": 1},
        5: {"name": "Fijación", "parent_id": 1},
        100: {"name": "DEYE", "parent_id": 6},
        101: {"name": "Huawei", "parent_id": 6},
        102: {"name": "Sungrow", "parent_id": 6},
        200: {"name": "JA", "parent_id": 7},
        201: {"name": "Astro 575", "parent_id": 7},
        202: {"name": "Astro 615", "parent_id": 7},
        300: {"name": "Cables", "parent_id": 8},
    }


def _lines_map():
    keys = [
        "deye", "huawei", "sungrow", "estructuras", "cables",
        "paneles_ja", "paneles_astro_575", "paneles_astro_615",
    ]
    return {k: f"line-{k}" for k in keys}


def test_normalize_name():
    assert _normalize_name("Fijación") == "fijacion"
    assert _normalize_name("ASTRO 575") == "astro 575"
    assert _normalize_name("paneles_astro_575") == "paneles astro 575"
    assert _normalize_name("  Almacenamiento / Deye  ") == "almacenamiento deye"
    assert _normalize_name("JA") == "ja"


def test_resolve_brand_subcategory():
    assert _resolve_product_line(100, _cat_map(), _lines_map()) == "line-deye"
    assert _resolve_product_line(101, _cat_map(), _lines_map()) == "line-huawei"
    assert _resolve_product_line(102, _cat_map(), _lines_map()) == "line-sungrow"


def test_resolve_cables_leaf_and_alias():
    assert _resolve_product_line(300, _cat_map(), _lines_map()) == "line-cables"
    assert _resolve_product_line(8, _cat_map(), _lines_map()) == "line-cables"


def test_resolve_fijacion_accent_alias():
    assert _resolve_product_line(5, _cat_map(), _lines_map()) == "line-estructuras"


def test_resolve_panels():
    assert _resolve_product_line(200, _cat_map(), _lines_map()) == "line-paneles_ja"
    assert _resolve_product_line(201, _cat_map(), _lines_map()) == "line-paneles_astro_575"
    assert _resolve_product_line(202, _cat_map(), _lines_map()) == "line-paneles_astro_615"


def test_leaf_takes_priority_over_parent():
    cat_map = _cat_map()
    cat_map[6] = {"name": "DEYE", "parent_id": 1}
    assert _resolve_product_line(100, cat_map, _lines_map()) == "line-deye"


def test_accessories_by_brand_fallback():
    assert _resolve_product_line(
        9, _cat_map(), _lines_map(), product_name="Huawei SDongleA-05"
    ) == "line-huawei"
    assert _resolve_product_line(
        9, _cat_map(), _lines_map(), product_name="Kit de 3 TI Sungrow 250A"
    ) == "line-sungrow"


def test_no_match_returns_none():
    assert _resolve_product_line(
        9, _cat_map(), _lines_map(), product_name="Smart Meter Eastron SDM 120 CTM"
    ) is None
    assert _resolve_product_line(None, _cat_map(), _lines_map(), product_name=None) is None


def test_inactive_line_not_used():
    lines = _lines_map()
    del lines["deye"]
    assert _resolve_product_line(100, _cat_map(), lines) is None
