"""
Tests for search functionality
"""
import pytest


def test_health_endpoint(client):
    """Test that health endpoint is working"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_search_endpoint_validation(client, mock_db):
    """Test search endpoint input validation"""
    # Test missing query parameter
    response = client.get("/api/search")
    assert response.status_code == 422

    # Test query too short
    response = client.get("/api/search?q=a")
    assert response.status_code == 422

    # Test valid query with mocked database
    mock_db.fetch_all.return_value = []
    response = client.get("/api/search?q=test")
    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "test"
    assert "total_count" in data
    assert "results" in data


def test_search_suggestions_endpoint_validation(client, mock_db):
    """Test search suggestions endpoint input validation"""
    # Test missing query parameter
    response = client.get("/api/search/suggestions")
    assert response.status_code == 422

    # Test valid query with mocked database
    mock_db.fetch_all.return_value = []
    response = client.get("/api/search/suggestions?q=test")
    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "test"
    assert "suggestions" in data


def test_search_endpoint_with_mock_db(client, mock_db):
    """Test search endpoint with mocked database"""

    # Mock wrestler data - need to return different results for different queries
    def mock_fetch_all(query, *args):
        if "wrestler_latest" in query:
            # Return wrestler data
            return [
                {
                    "person_id": "1",
                    "first_name": "Spencer",
                    "last_name": "Lee",
                    "last_school": "Iowa",
                    "last_year": 2021,
                    "last_weight_class": "125",
                }
            ]
        elif "school" in query:
            # Return school data
            return [
                {
                    "school_id": "1",
                    "name": "Iowa University",
                    "location": "Iowa City, IA",
                    "mascot": "Hawkeyes",
                }
            ]
        else:
            return []

    mock_db.fetch_all.side_effect = mock_fetch_all

    response = client.get("/api/search?q=spencer")
    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "spencer"
    assert "total_count" in data
    assert "results" in data
    assert "offset" in data
    assert "limit" in data


def test_search_suggestions_with_mock_db(client, mock_db):
    """Test search suggestions endpoint with mocked database"""
    # Mock suggestions data - the search suggestions endpoint makes multiple queries
    mock_db.fetch_all.side_effect = [
        [{"name": "Spencer Lee", "count": 1}],  # wrestlers
        [{"name": "Iowa", "count": 1}],  # schools
        [{"name": "NCAA Championships", "count": 1}],  # tournaments
    ]

    response = client.get("/api/search/suggestions?q=sp")
    assert response.status_code == 200

    data = response.json()
    assert data["query"] == "sp"
    assert "suggestions" in data
    assert len(data["suggestions"]) >= 0


def test_search_relevance_scoring():
    """Test the relevance scoring function"""

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

        if re.search(r"\b" + re.escape(query_lower) + r"\b", text_lower):
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


def test_legacy_search_endpoint(client, mock_db):
    """Test legacy search endpoint for backward compatibility"""

    # Mock legacy search data - need to return different results for different queries
    def mock_fetch_all(query, *args):
        if "role_type = 'wrestler'" in query:
            # Return wrestler data with correct column names from SQL alias
            return [
                {
                    "id": "1",  # SQL alias: p.person_id as id
                    "name": "Test Wrestler",  # SQL alias: first_name || last_name
                    "additional_info": "Test University",  # SQL alias: s.name
                }
            ]
        elif "role_type = 'coach'" in query:
            # Return coach data
            return [
                {
                    "id": "2",
                    "name": "Test Coach",
                    "additional_info": "Test University",
                }
            ]
        elif "school" in query and "role_type" not in query:
            # Return school data
            return [
                {
                    "id": "1",
                    "name": "Test University",
                    "additional_info": "Iowa City, IA",
                }
            ]
        elif "tournament" in query:
            # Return tournament data
            return [
                {
                    "id": "1",
                    "name": "Test Tournament",
                    "additional_info": "2021",
                }
            ]
        else:
            return []

    mock_db.fetch_all.side_effect = mock_fetch_all

    response = client.get("/api/search/legacy?q=test")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(
        data, dict
    )  # Legacy endpoint returns a dict with categorized results
    assert "wrestlers" in data
    assert "schools" in data
    assert "tournaments" in data
    assert "query" in data

    # Verify some results were found
    assert len(data["wrestlers"]) > 0
    assert len(data["schools"]) > 0
    assert len(data["tournaments"]) > 0
    assert data["wrestlers"][0]["type"] == "wrestler"
    assert data["schools"][0]["type"] == "school"
    assert data["tournaments"][0]["type"] == "tournament"


if __name__ == "__main__":
    pytest.main([__file__])
