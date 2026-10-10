import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_auth_registration(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "newuser@taskforge.dev",
            "password": "SecurePassword123!",
            "full_name": "New User",
            "role": "member"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "newuser@taskforge.dev"
    assert "set-cookie" in response.headers or "refresh_token" in data


@pytest.mark.asyncio
async def test_auth_login_success(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "dev@taskforge.dev",
            "password": "SecurePassword123!"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["role"] == "admin"
    assert "refresh_token" in response.cookies or data.get("refresh_token")


@pytest.mark.asyncio
async def test_auth_login_invalid_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "dev@taskforge.dev",
            "password": "WrongPassword!"
        }
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_auth_token_rotation(client: AsyncClient):
    # 1. Login to get refresh token
    login_res = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "dev@taskforge.dev",
            "password": "SecurePassword123!"
        }
    )
    refresh_token = login_res.json()["refresh_token"]

    # 2. Refresh token
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        params={"refresh_token_body": refresh_token}
    )
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data
