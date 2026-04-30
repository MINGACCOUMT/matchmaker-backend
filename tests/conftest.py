"""Pytest fixtures for matchmaker backend."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base, get_db
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def client():
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def auth_headers(client):
    """Register a user and return auth headers."""
    r = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "password": "test123",
        "nickname": "Tester",
        "gender": 1,
        "birth_date": "1990-01-01"
    })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def user_b(client):
    """Register a second user and return their auth headers."""
    r = client.post("/api/auth/register", json={
        "email": "b@example.com",
        "password": "test123",
        "nickname": "UserB",
        "gender": 2,
        "birth_date": "1995-01-01"
    })
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
