import pytest
from httpx import AsyncClient
from app.main import app
import asyncio


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.mark.anyio
async def test_root():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "Dating App API" in response.json()["data"]["name"]


@pytest.mark.anyio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


@pytest.mark.anyio
async def test_signup():
    """Test user signup."""
    user_data = {
        "email": "test@example.com",
        "password": "testpass123"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/signup", json=user_data)
    
    # First signup should succeed
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert "_id" in data
    
    # Second signup with same email should fail
    response2 = await ac.post("/api/v1/auth/signup", json=user_data)
    assert response2.status_code == 409


@pytest.mark.anyio
async def test_login():
    """Test user login."""
    user_data = {
        "email": "login_test@example.com",
        "password": "testpass123"
    }
    
    # Create user first
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/api/v1/auth/signup", json=user_data)
        
        # Login
        response = await ac.post("/api/v1/auth/login", json=user_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    user_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/login", json=user_data)
    
    assert response.status_code == 401
