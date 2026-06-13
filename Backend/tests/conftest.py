import os
os.environ["DISABLE_RATE_LIMIT"] = "true"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.models import User
from app.auth import hash_password, create_access_token
from app.main import app
from datetime import timedelta

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(autouse=True)
def _test_db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    admin = db.query(User).filter(User.username == "admin").first()
    if not admin:
        admin = User(
            email="admin@test.com",
            username="admin",
            name="Admin",
            role="admin",
            hashed_password=hash_password("admin123"),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    db.close()
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_token(client):
    resp = client.post("/auth/login", json={
        "username": "admin",
        "password": "admin123",
    })
    return resp.json()["access_token"]


@pytest.fixture
def admin_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}
