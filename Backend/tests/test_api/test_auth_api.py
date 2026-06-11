def test_health_endpoint(api_request_context):
    resp = api_request_context.get("/health")
    assert resp.status == 200
    assert resp.json() == {"status": "ok"}


def test_register_and_login(api_request_context):
    email = "e2e@test.com"
    username = "e2euser"
    password = "test123"

    resp = api_request_context.post("/auth/register", data={
        "email": email,
        "username": username,
        "name": "E2E User",
        "password": password,
    })
    assert resp.status == 201

    resp = api_request_context.post("/auth/login", data={
        "username": username,
        "password": password,
    })
    assert resp.status == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_fails_with_wrong_password(api_request_context):
    resp = api_request_context.post("/auth/login", data={
        "username": "nonexistent",
        "password": "wrongpass",
    })
    assert resp.status == 401


def test_protected_endpoint_without_token(api_request_context):
    resp = api_request_context.get("/auth/me")
    assert resp.status == 401
