import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import get_db, Base
from app import models
from datetime import date

# Setup Test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
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
    
    # Create valid child
    if not db.query(models.Child).filter(models.Child.child_id == 1).first():
        child = models.Child(child_id=1, name="TestChild", grade="1")
        db.add(child)
        db.commit()
        
    yield db
    Base.metadata.drop_all(bind=engine)

def test_get_home_data_success(test_db):
    response = client.get("/api/home/1")
    assert response.status_code == 200
    data = response.json()
    assert "missions" in data
    assert "last_results" in data
    assert "character_message" in data
    assert len(data["missions"]) == 4

def test_get_home_data_not_found(test_db):
    response = client.get("/api/home/999")
    assert response.status_code == 404

def test_character_message(test_db):
    response = client.get("/api/character/message/1")
    assert response.status_code == 200
    assert "message" in response.json()
