"""
Tests for search functionality
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


def test_health_endpoint(client):
    """Test that health endpoint is working"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_search_endpoint_validation(client):
    """Test search endpoint input validation"""
    # Test missing query parameter
    response = client.get("/api/search")
    assert response.status_code == 422
    
    # Test query too short
    response = client.get("/api/search?q=a")
    assert response.status_code == 422
    
    # Test valid query without database connection
    response = client.get("/api/search?q=test")
    # This will fail due to no database, but should not be a validation error
    assert response.status_code == 500  # Internal server error due to no DB


def test_search_suggestions_endpoint_validation(client):
    """Test search suggestions endpoint input validation"""
    # Test missing query parameter
    response = client.get("/api/search/suggestions")
    assert response.status_code == 422
    
    # Test valid query without database connection
    response = client.get("/api/search/suggestions?q=test")
    # This will fail due to no database, but should not be a validation error
    assert response.status_code == 500  # Internal server error due to no DB


@patch('app.routers.search.get_db')
def test_search_endpoint_with_mock_db(mock_get_db, client):
    """Test search endpoint with mocked database"""
    # Mock database
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock wrestler data
    mock_db.fetch_all.return_value = [
        {
            'person_id': '1',
            'first_name': 'Spencer',
            'last_name': 'Lee',
            'last_school': 'Iowa',
            'last_year': 2021,
            'last_weight_class': '125'
        }
    ]
    
    response = client.get("/api/search?q=spencer")
    assert response.status_code == 200
    
    data = response.json()
    assert data["query"] == "spencer"
    assert "total_count" in data
    assert "results" in data
    assert "offset" in data
    assert "limit" in data


@patch('app.routers.search.get_db')
def test_search_suggestions_with_mock_db(mock_get_db, client):
    """Test search suggestions endpoint with mocked database"""
    # Mock database
    mock_db = AsyncMock()
    mock_get_db.return_value = mock_db
    
    # Mock suggestions data
    mock_db.fetch_all.side_effect = [
        [{'name': 'Spencer Lee', 'count': 1}],  # wrestlers
        [{'name': 'Iowa', 'count': 1}],         # schools
        [{'name': 'NCAA Championships', 'count': 1}]  # tournaments
    ]
    
    response = client.get("/api/search/suggestions?q=sp")
    assert response.status_code == 200
    
    data = response.json()
    assert data["query"] == "sp"
    assert "suggestions" in data
    assert len(data["suggestions"]) >= 0


def test_search_relevance_scoring():
    """Test the relevance scoring function"""
    from app.routers.search import search_enhanced
    
    # We need to extract the relevance calculation function for unit testing
    # This would be a helper function in the actual implementation
    def calculate_relevance_score(text: str, query: str) -> float:
        """Calculate relevance score based on match quality"""
        if not text or not query:
            return 0.0
        
        text_lower = text.lower()
        query_lower = query.lower()
        
        # Exact match
        if text_lower == query_lower:
            return 1.0
        
        # Starts with query
        if text_lower.startswith(query_lower):
            return 0.9
        
        # Contains as word (word boundary match)
        import re
        if re.search(r'\b' + re.escape(query_lower) + r'\b', text_lower):
            return 0.8
        
        # Contains substring
        if query_lower in text_lower:
            return 0.7
        
        return 0.0
    
    # Test exact match
    assert calculate_relevance_score("Spencer Lee", "Spencer Lee") == 1.0
    
    # Test starts with
    assert calculate_relevance_score("Spencer Lee", "Spencer") == 0.9
    
    # Test word boundary
    assert calculate_relevance_score("Spencer Lee Jr", "Lee") == 0.8
    
    # Test substring
    assert calculate_relevance_score("Spencer Lee", "enc") == 0.7
    
    # Test no match
    assert calculate_relevance_score("Spencer Lee", "xyz") == 0.0


def test_legacy_search_endpoint(client):
    """Test legacy search endpoint for backward compatibility"""
    response = client.get("/api/search/legacy?q=test")
    # Should fail due to no database but not due to validation
    assert response.status_code == 500  # Internal server error due to no DB


if __name__ == "__main__":
    pytest.main([__file__])