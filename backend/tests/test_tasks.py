import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_project_tasks(client: AsyncClient, admin_token: str):
    project_id = "b1111111-1111-1111-1111-111111111111"
    response = await client.get(
        f"/api/v1/projects/{project_id}/tasks",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) >= 1
    assert any(t["title"] == "Implement Auth Pipeline" for t in tasks)


@pytest.mark.asyncio
async def test_patch_task_status_transition(client: AsyncClient, admin_token: str):
    task_id = "c1111111-1111-1111-1111-111111111111"
    
    # 1. Update status to in_progress
    response = await client.patch(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "status": "in_progress",
            "assignee_id": "a3bb189e-8bf9-3888-9912-ace4e6543002"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    assert data["assignee_id"] == "a3bb189e-8bf9-3888-9912-ace4e6543002"

    # 2. Re-fetch task to verify persistence
    get_res = await client.get(
        f"/api/v1/tasks/{task_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_res.status_code == 200
    assert get_res.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_create_task_admin(client: AsyncClient, admin_token: str):
    project_id = "b1111111-1111-1111-1111-111111111111"
    response = await client.post(
        "/api/v1/tasks",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "project_id": project_id,
            "title": "Setup Automated Playwright E2E Suite",
            "description": "Integration testing layer for Kanban UI updates",
            "status": "todo",
            "priority": "high"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Setup Automated Playwright E2E Suite"
    assert data["status"] == "todo"
