import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app import models

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_settings.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    Base.metadata.drop_all(bind=engine)

def test_get_settings_create_default(test_db):
    # Should create default parent and settings
    response = client.get("/api/settings/1")
    assert response.status_code == 200
    data = response.json()
    assert data["parent_id"] == 1
    assert data["voice_enabled"] is True

def test_add_child_and_auto_select(test_db):
    response = client.post("/api/child/add", json={
        "parent_id": 1,
        "name": "TestChild",
        "age": 7,
        "grade": "Sho-1"
    })
    assert response.status_code == 200
    child_id = response.json()["child_id"]

    # Verify settings auto-selected this child
    settings_res = client.get("/api/settings/1")
    assert settings_res.json()["child_id"] == child_id

def test_update_settings(test_db):
    response = client.put("/api/settings/1", json={"voice_enabled": False})
    assert response.status_code == 200
    assert response.json()["voice_enabled"] is False

def test_update_child(test_db):
    # Get child id first
    children = client.get("/api/child/all/1").json()
    child_id = children[0]["child_id"]

    response = client.put(f"/api/child/{child_id}", json={"name": "UpdatedName"})
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedName"
