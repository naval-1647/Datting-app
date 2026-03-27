from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
import logging

from app.schemas.profile import ProfileResponse
from app.services.profile_service import ProfileService
from app.models.user import UserInDB
from app.dependencies import get_current_user
from app.middleware import NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/search")
async def search_users(
    q: Optional[str] = None,
    age_min: Optional[int] = Query(None, ge=18, le=120),
    age_max: Optional[int] = Query(None, ge=18, le=120),
    gender: Optional[str] = None,
    interests: Optional[str] = None,
    location: Optional[str] = None,  # Format: "lat,lng"
    radius_km: Optional[float] = Query(None, ge=1, le=1000),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Search users with filters.
    
    **Query Parameters:**
    - `q`: Text search in name/bio
    - `age_min`: Minimum age
    - `age_max`: Maximum age
    - `gender`: Filter by gender
    - `interests`: Comma-separated interests
    - `location`: Location as "latitude,longitude"
    - `radius_km`: Search radius in kilometers
    - `page`: Page number
    - `limit`: Results per page
    """
    try:
        # Parse interests
        interests_list = None
        if interests:
            interests_list = [i.strip() for i in interests.split(",")]
        
        # Parse location
        location_coords = None
        if location:
            try:
                lat, lng = location.split(",")
                location_coords = [float(lng.strip()), float(lat.strip())]  # GeoJSON format
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid location format. Use 'lat,lng'"
                )
        
        # Calculate skip
        skip = (page - 1) * limit
        
        # Search profiles
        profiles = await ProfileService.search_profiles(
            query=q,
            age_min=age_min,
            age_max=age_max,
            gender=gender,
            interests=interests_list,
            location=location_coords,
            radius_km=radius_km,
            skip=skip,
            limit=limit
        )
        
        # Get total count (approximate)
        total = len(profiles)
        
        return {
            "success": True,
            "data": profiles,
            "pagination": {
                "page": page,
                "limit": limit,
                "total": total,
                "has_more": total == limit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching users: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_users(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """List all users (admin functionality)."""
    from app.services.user_service import UserService
    
    skip = (page - 1) * limit
    users = await UserService.get_all_users(skip, limit)
    
    return {
        "success": True,
        "data": users,
        "pagination": {
            "page": page,
            "limit": limit,
            "has_more": len(users) == limit
        }
    }
