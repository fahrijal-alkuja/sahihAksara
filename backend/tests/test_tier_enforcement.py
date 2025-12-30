import pytest
from fastapi.testclient import TestClient
from main import app
import models
import database
from sqlalchemy.orm import Session
import datetime

client = TestClient(app)

# Helper to get DB
def get_db():
    db = database.SessionLocal()
    try:
        return db
    finally:
        db.close()

@pytest.fixture
def db_session():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_user(db_session):
    user_email = "test_test@example.com"
    user = db_session.query(models.User).filter(models.User.email == user_email).first()
    if not user:
        user = models.User(
            email=user_email,
            hashed_password="hashed_dummy",
            full_name="Test User",
            role="free",
            daily_quota=5
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
    return user

def get_token(email):
    from core.auth import create_access_token
    return create_access_token(data={"sub": email})

def test_free_user_word_limit(test_user, db_session):
    # Ensure role is free
    test_user.role = "free"
    db_session.commit()
    
    token = get_token(test_user.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # 1. Test within limit (valid)
    long_text = " ".join(["kata"] * 100)
    response = client.post("/analyze", json={"text_content": long_text}, headers=headers)
    assert response.status_code == 200
    
    # 2. Test over limit (> 800 words)
    too_long_text = " ".join(["kata"] * 850)
    response = client.post("/analyze", json={"text_content": too_long_text}, headers=headers)
    assert response.status_code == 403
    assert "Batas gratis 800 kata terlampaui" in response.json()["detail"]

def test_free_user_quota_enforcement(test_user, db_session):
    test_user.role = "free"
    test_user.daily_quota = 1
    db_session.commit()
    
    token = get_token(test_user.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # First scan should pass
    response = client.post("/analyze", json={"text_content": "Cek kuota satu dua tiga empat lima enam tujuh delapan sembilan sepuluh."}, headers=headers)
    assert response.status_code == 200
    
    # Second scan should fail (quota 0)
    response = client.post("/analyze", json={"text_content": "Cek kuota lagi."}, headers=headers)
    assert response.status_code == 403
    assert "Kuota harian gratis Anda sudah habis" in response.json()["detail"]

def test_doc_upload_for_free_user_within_limit(test_user, db_session):
    test_user.role = "free"
    test_user.daily_quota = 5
    db_session.commit()
    
    token = get_token(test_user.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Mocking a small file upload
    content = b"Ini adalah isi file test sederhana untuk user gratis."
    files = {"file": ("test.txt", content, "text/plain")}
    
    response = client.post("/analyze-file", files=files, headers=headers)
    assert response.status_code == 200
    
    # Check if quota was deducted
    db_session.refresh(test_user)
    assert test_user.daily_quota == 4

def test_pro_user_unlimited_access(test_user, db_session):
    # Set to pro with future expiry to avoid auto-downgrade
    test_user.role = "pro"
    test_user.daily_quota = 99999
    test_user.pro_expires_at = datetime.datetime.utcnow() + datetime.timedelta(days=30)
    db_session.commit()
    
    token = get_token(test_user.email)
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test very long text (> 800 words)
    very_long_text = " ".join(["pro_kata"] * 1000)
    response = client.post("/analyze", json={"text_content": very_long_text}, headers=headers)
    
    # Should pass for Pro
    assert response.status_code == 200
    assert response.json()["ai_probability"] is not None
    assert response.json().get("partially_analyzed") is False

@pytest.fixture(autouse=True)
def cleanup_test_user(db_session):
    yield
    user = db_session.query(models.User).filter(models.User.email == "test_test@example.com").first()
    if user:
        db_session.query(models.ScanResult).filter(models.ScanResult.user_id == user.id).delete()
        db_session.delete(user)
        db_session.commit()
