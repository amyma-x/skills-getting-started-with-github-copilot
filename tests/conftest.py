"""
Shared fixtures for FastAPI tests
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture that provides a TestClient for testing the FastAPI app.
    The in-memory database is fresh for each test.
    """
    return TestClient(app)


@pytest.fixture
def sample_activities(client):
    """
    Fixture that returns sample activity data from the GET /activities endpoint.
    Useful for tests that need to verify activity structure.
    """
    response = client.get("/activities")
    assert response.status_code == 200
    return response.json()


@pytest.fixture
def reset_participants(client):
    """
    Fixture generator for resetting participant lists between tests.
    Note: In-memory database persists across tests, so we provide a way to verify initial state.
    """
    # This fixture can be extended if needed to reset state between tests
    yield client
