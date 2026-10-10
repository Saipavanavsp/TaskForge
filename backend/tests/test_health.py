import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_liveness(client: AsyncClient):
    response = await client.get("/api/v1/healthz/liveness")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_readiness(client: AsyncClient):
    response = await client.get("/api/v1/healthz/readiness")
    # Readiness should return 200 when DB is connected
    assert response.status_code == 200
    data = response.json()
    assert "database" in data


@pytest.mark.asyncio
async def test_metrics_endpoint(client: AsyncClient):
    response = await client.get("/metrics")
    assert response.status_code == 200
    assert "http_requests_total" in response.text
