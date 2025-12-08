import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db, Base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from time import sleep

# Use same test db setup logic
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_screentime.db"
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
    yield
    Base.metadata.drop_all(bind=engine)

def test_start_screentime(test_db):
    response = client.post("/api/screentime/start", json={"child_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True
    assert data["elapsed_seconds"] == 0

def test_resume_screentime(test_db):
    # Simulate time passing? Hard in integration test without mocking datetime
    # But we can check if calling start again resumes the same session
    res1 = client.post("/api/screentime/start", json={"child_id": 1})
    id1 = res1.json()["screentime_id"]
    
    res2 = client.post("/api/screentime/start", json={"child_id": 1})
    id2 = res2.json()["screentime_id"]
    
    assert id1 == id2 # Should resume same ID

def test_status_update(test_db):
    response = client.get("/api/screentime/status?child_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is True
    # Elapsed might be > 0 if time passed
    assert data["elapsed_seconds"] >= 0

def test_end_screentime(test_db):
    response = client.post("/api/screentime/end", json={"child_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["end_time"] is not None
    assert data["total_minutes"] is not None

def test_status_after_end(test_db):
    response = client.get("/api/screentime/status?child_id=1")
    assert response.status_code == 200
    data = response.json()
    assert data["is_active"] is False
