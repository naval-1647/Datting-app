import pytest
from httpx import AsyncClient
from app.main import app


@pytest.mark.anyio
async def test_swipe_like():
    """Test swiping right (like)."""
    # Create two users
    user1_data = {"email": "swiper@example.com", "password": "testpass123"}
    user2_data = {"email": "swipee@example.com", "password": "testpass123"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Setup user 1
        await ac.post("/api/v1/auth/signup", json=user1_data)
        login1 = await ac.post("/api/v1/auth/login", json=user1_data)
        token1 = login1.json()["access_token"]
        
        # Setup user 2
        await ac.post("/api/v1/auth/signup", json=user2_data)
        login2 = await ac.post("/api/v1/auth/login", json=user2_data)
        token2 = login2.json()["access_token"]
        
        # Create profiles for both users
        profile2_data = {
            "name": "User 2",
            "age": 26,
            "gender": "female",
            "location": {"type": "Point", "coordinates": [-73.935242, 40.730610]}
        }
        await ac.post("/api/v1/profiles/", json=profile2_data, headers={"Authorization": f"Bearer {token2}"})
        
        # Get user 2's profile to get user_id
        profile_response = await ac.get("/api/v1/profiles/me", headers={"Authorization": f"Bearer {token2}"})
        user2_id = profile_response.json()["user_id"]
        
        # User 1 swipes right on user 2
        swipe_data = {"target_user_id": user2_id, "action": "like"}
        response = await ac.post(
            "/api/v1/swipes/",
            json=swipe_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
    
    assert response.status_code == 201
    data = response.json()
    assert data["action"] == "like"
    assert data["target_user_id"] == user2_id


@pytest.mark.anyio
async def test_duplicate_swipe_prevention():
    """Test that duplicate swipes are prevented."""
    user1_data = {"email": "dup_swiper@example.com", "password": "testpass123"}
    user2_data = {"email": "dup_swipee@example.com", "password": "testpass123"}
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Setup users
        await ac.post("/api/v1/auth/signup", json=user1_data)
        login1 = await ac.post("/api/v1/auth/login", json=user1_data)
        token1 = login1.json()["access_token"]
        
        await ac.post("/api/v1/auth/signup", json=user2_data)
        login2 = await ac.post("/api/v1/auth/login", json=user2_data)
        token2 = login2.json()["access_token"]
        
        # Create profile
        profile_data = {
            "name": "User 2",
            "age": 27,
            "gender": "male",
            "location": {"type": "Point", "coordinates": [-74.0060, 40.7128]}
        }
        await ac.post("/api/v1/profiles/", json=profile_data, headers={"Authorization": f"Bearer {token2}"})
        
        profile_response = await ac.get("/api/v1/profiles/me", headers={"Authorization": f"Bearer {token2}"})
        user2_id = profile_response.json()["user_id"]
        
        # First swipe
        swipe_data = {"target_user_id": user2_id, "action": "dislike"}
        await ac.post("/api/v1/swipes/", json=swipe_data, headers={"Authorization": f"Bearer {token1}"})
        
        # Second swipe (should fail)
        response2 = await ac.post(
            "/api/v1/swipes/",
            json=swipe_data,
            headers={"Authorization": f"Bearer {token1}"}
        )
    
    assert response2.status_code == 409  # Conflict
