"""
Test configuration and fixtures
"""
import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def client():
    """Test client for synchronous tests"""
    return TestClient(app)


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
