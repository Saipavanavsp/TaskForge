import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_projects(client: AsyncClient, admin_token: str):
    response = await client.get(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    projects = response.json()
    assert len(projects) >= 1
    assert any(p["slug"] == "core-platform" for p in projects)


@pytest.mark.asyncio
async def test_create_project_admin_success(client: AsyncClient, admin_token: str):
    response = await client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "title": "Cloud S3 Storage Module",
            "slug": "cloud-s3-storage",
            "description": "MinIO object storage integration"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Cloud S3 Storage Module"
    assert data["slug"] == "cloud-s3-storage"


@pytest.mark.asyncio
async def test_create_project_member_forbidden(client: AsyncClient, member_token: str):
    # Members should NOT be allowed to create projects (RBAC test)
    response = await client.post(
        "/api/v1/projects",
        headers={"Authorization": f"Bearer {member_token}"},
        json={
            "title": "Unauthorized Project",
            "slug": "unauthorized-project",
            "description": "Should fail with 403"
        }
    )
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]
