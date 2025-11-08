import pytest
from fastapi.testclient import TestClient
from api import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_search_success():
    response = client.post("/search", json={"query": "test query"})
    assert response.status_code == 200
    assert len(response.json()) > 0

@pytest.mark.asyncio
async def test_search_invalid_search_type():
    response = client.post("/search", json={"query": "test query", "search_type": "invalid"})
    assert response.status_code == 422
