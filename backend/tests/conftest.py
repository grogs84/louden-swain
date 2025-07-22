"""
Test configuration and fixtures
"""
import asyncio
import os
from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Set test database URL before importing the app
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test.db"

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_db():
    """Mock database for testing"""
    db_mock = AsyncMock()
    # Mock successful connection
    db_mock.connect.return_value = None
    return db_mock


@pytest.fixture
def client(mock_db):
    """Test client for synchronous tests with mocked database"""
    from app.database import get_db

    # Override the dependency
    def override_get_db():
        return mock_db

    app.dependency_overrides[get_db] = override_get_db

    client = TestClient(app)
    yield client

    # Clean up
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Async test client for asynchronous tests"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture
def test_data():
    """Sample test data"""
    return {
        "tournament": {
            "name": "Test Tournament",
            "year": 2024,
            "location": "Test Location",
        },
        "participant": {
            "name": "Test Wrestler",
            "weight_class": "125",
            "school": "Test University",
        },
    }
