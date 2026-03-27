from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from typing import List
import logging

from app.schemas.profile import ProfileCreate, ProfileUpdate, ProfileResponse, ProfileWithDistance
from app.services.profile_service import ProfileService
from app.services.storage_service import StorageService
from app.models.user import UserInDB
from app.dependencies import get_current_user, validate_user_profile_exists
from app.middleware import NotFoundException, ValidationException
from app.database import db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create a new user profile."""
    try:
        # Check if profile already exists
        existing = await ProfileService.get_profile_by_user_id(str(current_user.id))
        if existing:
            raise ValidationException("Profile already exists")
        
        # Set user_id from authenticated user
        profile_data.user_id = str(current_user.id)
        
        profile = await ProfileService.create_profile(profile_data)
        
        if not profile:
            raise HTTPException(status_code=500, detail="Failed to create profile")
        
        logger.info(f"Profile created for user {current_user.email}")
        return profile
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/me", response_model=ProfileResponse)
async def get_my_profile(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's profile."""
    profile = await ProfileService.get_profile_by_user_id(str(current_user.id))
    
    if not profile:
        raise NotFoundException("Profile not found. Create your profile first.")
    
    return profile


@router.put("/me", response_model=ProfileResponse)
async def update_my_profile(
    profile_update: ProfileUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update current user's profile."""
    profile = await ProfileService.update_profile(str(current_user.id), profile_update)
    
    if not profile:
        raise NotFoundException("Profile not found")
    
    return profile


@router.post("/me/images", response_model=ProfileResponse)
async def upload_profile_images(
    files: List[UploadFile] = File(...),
    current_user: UserInDB = Depends(get_current_user)
):
    """Upload profile images (max 5)."""
    try:
        # Validate file count
        if len(files) > 5:
            raise ValidationException("Maximum 5 images allowed")
        
        # Get current profile
        profile = await ProfileService.get_profile_by_user_id(str(current_user.id))
        if not profile:
            raise NotFoundException("Profile not found")
        
        # Check image limit
        if len(profile.images) + len(files) > 10:
            raise ValidationException("Maximum 10 images per profile")
        
        # Upload images
        uploaded_urls = await StorageService.upload_multiple_images(files, "profiles")
        
        if not uploaded_urls:
            raise HTTPException(status_code=500, detail="Image upload failed")
        
        # Add URLs to profile
        for url in uploaded_urls:
            await ProfileService.add_profile_image(str(current_user.id), url)
        
        # Return updated profile
        updated_profile = await ProfileService.get_profile_by_user_id(str(current_user.id))
        return updated_profile
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error uploading images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me/images/{image_index}", response_model=ProfileResponse)
async def delete_profile_image(
    image_index: int,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a profile image by index."""
    profile = await ProfileService.get_profile_by_user_id(str(current_user.id))
    
    if not profile:
        raise NotFoundException("Profile not found")
    
    if image_index < 0 or image_index >= len(profile.images):
        raise ValidationException("Invalid image index")
    
    # Get image URL
    image_url = profile.images[image_index]
    
    # Delete from storage
    await StorageService.delete_image(image_url)
    
    # Remove from profile
    await ProfileService.remove_profile_image(str(current_user.id), image_url)
    
    # Return updated profile
    updated_profile = await ProfileService.get_profile_by_user_id(str(current_user.id))
    return updated_profile


@router.get("/{user_id}", response_model=ProfileResponse)
async def get_user_profile(user_id: str, current_user: UserInDB = Depends(get_current_user)):
    """Get another user's profile by user ID."""
    profile = await ProfileService.get_profile_by_user_id(user_id)
    
    if not profile:
        raise NotFoundException("Profile not found")
    
    return profile
