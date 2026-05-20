"""Tests for authentication and user endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "Password123!",
            "full_name": "Test User",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "data" in data
    assert data["data"]["email"] == "test@example.com"
    assert data["data"]["full_name"] == "Test User"
    assert data["data"]["role"] == "user"
    assert "id" in data["data"]


@pytest.mark.asyncio
async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with an already existing email."""
    # First registration
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "Password123!",
        },
    )

    # Second registration with same email
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "dup@example.com",
            "password": "Password123!",
        },
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "conflict"


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Test login with valid credentials."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "login@example.com",
            "password": "Password123!",
        },
    )

    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "login@example.com",
            "password": "Password123!",
        },
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    """Test fetching current user profile using JWT."""
    # Register and login
    await client.post(
        "/api/v1/auth/register",
        json={
            "email": "me@example.com",
            "password": "Password123!",
            "full_name": "Me User",
        },
    )
    login_response = await client.post(
        "/api/v1/auth/login",
        json={
            "email": "me@example.com",
            "password": "Password123!",
        },
    )
    token = login_response.json()["data"]["access_token"]

    # Fetch profile
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email"] == "me@example.com"
    assert data["full_name"] == "Me User"


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    """Test accessing protected route without a token."""
    response = await client.get("/api/v1/users/me")
    assert response.status_code == 401
