def test_list_bands(client, admin_headers):
    resp = client.get("/discount-rules/bands", headers=admin_headers)
    assert resp.status_code == 200
    bands = resp.json()
    amount = [b for b in bands if b["condition_type"] == "amount"]
    qty = [b for b in bands if b["condition_type"] == "qty"]
    assert any(b["key"] == "gt_50000" and b["max"] is None for b in amount)
    assert any(b["key"] == "container" and b["max"] is None for b in qty)


def test_create_and_update_product_line(client, admin_headers):
    resp = client.post(
        "/discount-rules/product-lines",
        json={"key": "prueba_line", "name": "Línea de prueba"},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    line = resp.json()
    line_id = line["id"]
    assert line["key"] == "prueba_line"
    assert line["is_active"] is True

    resp = client.put(
        f"/discount-rules/product-lines/{line_id}",
        json={"name": "Línea renombrada", "is_active": False},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Línea renombrada"
    assert resp.json()["is_active"] is False


def test_duplicate_product_line_key_conflicts(client, admin_headers):
    client.post(
        "/discount-rules/product-lines",
        json={"key": "dup", "name": "Dup"},
        headers=admin_headers,
    )
    resp = client.post(
        "/discount-rules/product-lines",
        json={"key": "dup", "name": "Dup 2"},
        headers=admin_headers,
    )
    assert resp.status_code == 409


def test_create_rule_and_clear_open_band(client, admin_headers):
    line = client.post(
        "/discount-rules/product-lines",
        json={"key": "open_line", "name": "Open"},
        headers=admin_headers,
    ).json()

    resp = client.post(
        "/discount-rules",
        json={
            "seller_type": "vendedor_interno",
            "product_line_id": line["id"],
            "condition_type": "amount",
            "min_value": 50000.0,
            "max_value": 60000.0,
            "max_discount": 15.0,
            "requires_approval": False,
        },
        headers=admin_headers,
    )
    assert resp.status_code == 200
    rule = resp.json()
    rule_id = rule["id"]
    assert rule["product_line_key"] == "open_line"

    resp = client.put(
        f"/discount-rules/{rule_id}",
        json={"max_value": None, "max_discount": 20.0},
        headers=admin_headers,
    )
    assert resp.status_code == 200
    updated = resp.json()
    assert updated["max_value"] is None
    assert updated["max_discount"] == 20.0


def test_list_rules_include_inactive(client, admin_headers):
    line = client.post(
        "/discount-rules/product-lines",
        json={"key": "line_x", "name": "Línea X"},
        headers=admin_headers,
    ).json()
    rule = client.post(
        "/discount-rules",
        json={
            "seller_type": "vendedor_interno",
            "product_line_id": line["id"],
            "condition_type": "amount",
            "min_value": 0.0,
            "max_value": 500.0,
            "max_discount": 0.0,
            "requires_approval": False,
        },
        headers=admin_headers,
    ).json()

    client.delete(f"/discount-rules/{rule['id']}", headers=admin_headers)

    active = client.get("/discount-rules", headers=admin_headers).json()
    assert all(r["is_active"] for r in active)

    all_rules = client.get(
        "/discount-rules", params={"include_inactive": "true"}, headers=admin_headers
    ).json()
    assert any(r["id"] == rule["id"] and not r["is_active"] for r in all_rules)
