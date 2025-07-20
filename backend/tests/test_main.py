"""
Test main application endpoints
"""
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["message"] == "Wrestling Tournament Management API"
    assert "meta" in data
    assert "version" in data["meta"]


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert data["data"]["status"] == "healthy"
    assert data["data"]["service"] == "wrestling-tournament-api"


def test_api_docs():
    """Test API documentation is accessible"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
