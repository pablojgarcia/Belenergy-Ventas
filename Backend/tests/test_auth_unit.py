def test_register(client, admin_headers):
    resp = client.post("/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "name": "Test User",
        "password": "test123",
    }, headers=admin_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"
    assert "id" in data


def test_register_duplicate_email(client, admin_headers):
    client.post("/auth/register", json={
        "email": "dup@example.com",
        "username": "user1",
        "name": "User 1",
        "password": "test123",
    }, headers=admin_headers)
    resp = client.post("/auth/register", json={
        "email": "dup@example.com",
        "username": "user2",
        "name": "User 2",
        "password": "test123",
    }, headers=admin_headers)
    assert resp.status_code == 400
    assert "email" in resp.json()["detail"].lower()


def test_register_duplicate_username(client, admin_headers):
    client.post("/auth/register", json={
        "email": "a@example.com",
        "username": "dupuser",
        "name": "User A",
        "password": "test123",
    }, headers=admin_headers)
    resp = client.post("/auth/register", json={
        "email": "b@example.com",
        "username": "dupuser",
        "name": "User B",
        "password": "test123",
    }, headers=admin_headers)
    assert resp.status_code == 400
    assert "usuario" in resp.json()["detail"].lower()


def test_register_requires_admin(client):
    resp = client.post("/auth/register", json={
        "email": "noauth@example.com",
        "username": "noauth",
        "name": "No Auth",
        "password": "test123",
    })
    assert resp.status_code == 403


def test_login_success(client, admin_headers):
    client.post("/auth/register", json={
        "email": "login@example.com",
        "username": "loginuser",
        "name": "Login User",
        "password": "test123",
    }, headers=admin_headers)
    resp = client.post("/auth/login", json={
        "username": "loginuser",
        "password": "test123",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, admin_headers):
    client.post("/auth/register", json={
        "email": "wrongpw@example.com",
        "username": "wrongpw",
        "name": "Wrong PW",
        "password": "test123",
    }, headers=admin_headers)
    resp = client.post("/auth/login", json={
        "username": "wrongpw",
        "password": "wrongpass",
    })
    assert resp.status_code == 401


def test_login_nonexistent_user(client):
    resp = client.post("/auth/login", json={
        "username": "nobody",
        "password": "test123",
    })
    assert resp.status_code == 401


def test_me_authenticated(client, admin_headers):
    client.post("/auth/register", json={
        "email": "me@example.com",
        "username": "meuser",
        "name": "Me User",
        "password": "test123",
    }, headers=admin_headers)
    login_resp = client.post("/auth/login", json={
        "username": "meuser",
        "password": "test123",
    })
    token = login_resp.json()["access_token"]
    resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "meuser"
    assert resp.json()["role"] == "vendedor"


def test_me_unauthenticated(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 403


def test_refresh_token(client, admin_headers):
    client.post("/auth/register", json={
        "email": "refresh@example.com",
        "username": "refreshuser",
        "name": "Refresh User",
        "password": "test123",
    }, headers=admin_headers)
    login_resp = client.post("/auth/login", json={
        "username": "refreshuser",
        "password": "test123",
    })
    refresh_token = login_resp.json()["refresh_token"]
    resp = client.post("/auth/refresh", json={
        "refresh_token": refresh_token,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_refresh_invalid_token(client):
    resp = client.post("/auth/refresh", json={
        "refresh_token": "invalidtoken123",
    })
    assert resp.status_code == 401


def test_register_requires_admin(client):
    resp = client.post("/auth/register", json={
        "email": "noauth@example.com",
        "username": "noauth",
        "name": "No Auth",
        "password": "test123",
    })
    assert resp.status_code == 403


def test_admin_endpoints_blocked_for_vendedor(client, admin_headers):
    client.post("/auth/register", json={
        "email": "vendedor@test.com",
        "username": "vendedor",
        "name": "Vendedor",
        "password": "test123",
        "role": "vendedor",
    }, headers=admin_headers)
    login_vendedor = client.post("/auth/login", json={
        "username": "vendedor",
        "password": "test123",
    })
    vendedor_token = login_vendedor.json()["access_token"]
    resp = client.post("/sync/customers", headers={"Authorization": f"Bearer {vendedor_token}"})
    assert resp.status_code == 403
