import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.anyio
async def test_create_profile():
    """Test profile creation."""
    # First login to get token
    auth_data = {
        "email": "profile_test@example.com",
        "password": "testpass123"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Signup
        await ac.post("/api/v1/auth/signup", json=auth_data)
        
        # Login
        login_response = await ac.post("/api/v1/auth/login", json=auth_data)
        token = login_response.json()["access_token"]
        
        # Create profile
        profile_data = {
            "name": "Test User",
            "age": 25,
            "gender": "other",
            "bio": "Test bio",
            "interests": ["reading", "coding"],
            "location": {
                "type": "Point",
                "coordinates": [-73.935242, 40.730610]
            }
        }
        
        headers = {"Authorization": f"Bearer {token}"}
        response = await ac.post("/api/v1/profiles/", json=profile_data, headers=headers)
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == profile_data["name"]
    assert data["age"] == profile_data["age"]
    assert "user_id" in data


@pytest.mark.anyio
async def test_get_my_profile():
    """Test getting current user's profile."""
    auth_data = {
        "email": "get_profile_test@example.com",
        "password": "testpass123"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/api/v1/auth/signup", json=auth_data)
        
        login_response = await ac.post("/api/v1/auth/login", json=auth_data)
        token = login_response.json()["access_token"]
        
        # Create profile first
        profile_data = {
            "name": "Get Test",
            "age": 30,
            "gender": "male",
            "location": {
                "type": "Point",
                "coordinates": [-74.0060, 40.7128]
            }
        }
        await ac.post("/api/v1/profiles/", json=profile_data, headers={"Authorization": f"Bearer {token}"})
        
        # Get profile
        response = await ac.get("/api/v1/profiles/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == profile_data["name"]


@pytest.mark.anyio
async def test_update_profile():
    """Test updating profile."""
    auth_data = {
        "email": "update_profile_test@example.com",
        "password": "testpass123"
    }
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        await ac.post("/api/v1/auth/signup", json=auth_data)
        
        login_response = await ac.post("/api/v1/auth/login", json=auth_data)
        token = login_response.json()["access_token"]
        
        # Create profile
        profile_data = {
            "name": "Update Test",
            "age": 28,
            "gender": "female",
            "location": {
                "type": "Point",
                "coordinates": [-118.2437, 34.0522]
            }
        }
        await ac.post("/api/v1/profiles/", json=profile_data, headers={"Authorization": f"Bearer {token}"})
        
        # Update profile
        update_data = {
            "bio": "Updated bio",
            "interests": ["traveling", "cooking"]
        }
        response = await ac.put(
            "/api/v1/profiles/me",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["bio"] == update_data["bio"]
    assert data["interests"] == update_data["interests"]
