from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
import logging

from app.schemas.swipe import SwipeCreate, SwipeResponse, SwipeAction
from app.schemas.profile import ProfileWithDistance
from app.services.swipe_service import SwipeService
from app.services.match_service import MatchService
from app.services.profile_service import ProfileService
from app.services.notification_service import NotificationService
from app.models.user import UserInDB
from app.dependencies import get_current_user
from app.middleware import ValidationException, ConflictException
from app.database import db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/", response_model=SwipeResponse, status_code=status.HTTP_201_CREATED)
async def create_swipe(
    swipe_data: SwipeCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Swipe left (dislike) or right (like) on a user."""
    try:
        # Check if already swiped
        has_swiped = await SwipeService.has_already_swiped(
            str(current_user.id),
            swipe_data.target_user_id
        )
        
        if has_swiped:
            raise ConflictException("You have already swiped on this user")
        
        # Create swipe
        swipe_data.user_id = str(current_user.id)
        swipe = await SwipeService.create_swipe(swipe_data)
        
        if not swipe:
            raise HTTPException(status_code=500, detail="Failed to create swipe")
        
        # If it's a like, check for match
        if swipe_data.action == SwipeAction.LIKE:
            is_match = await SwipeService.check_match(
                str(current_user.id),
                swipe_data.target_user_id
            )
            
            if is_match:
                # Create match
                await MatchService.create_match(
                    str(current_user.id),
                    swipe_data.target_user_id
                )
                
                # Send notifications
                await NotificationService.create_notification(
                    swipe_data.target_user_id,
                    "new_match",
                    {"matched_with": str(current_user.id)}
                )
                
                await NotificationService.create_notification(
                    str(current_user.id),
                    "new_match",
                    {"matched_with": swipe_data.target_user_id}
                )
                
                logger.info(f"Match created between {current_user.id} and {swipe_data.target_user_id}")
        
        return swipe
        
    except ConflictException:
        raise
    except Exception as e:
        logger.error(f"Error creating swipe: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions", response_model=List[ProfileWithDistance])
async def get_suggested_users(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get suggested users based on matching algorithm."""
    try:
        # Get current user's profile
        current_profile = await ProfileService.get_profile_by_user_id(str(current_user.id))
        
        if not current_profile:
            raise ValidationException("Profile not found. Create your profile first.")
        
        # Get suggestions
        suggestions = await SwipeService.suggest_users(
            str(current_user.id),
            dict(current_profile),
            limit
        )
        
        return suggestions
        
    except ValidationException:
        raise
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=List[SwipeResponse])
async def get_swipe_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get user's swipe history."""
    swipes = await SwipeService.get_swipe_history(
        str(current_user.id),
        skip,
        limit
    )
    
    return swipes


@router.get("/check/{target_user_id}")
async def check_swipe_status(
    target_user_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Check if user has already swiped on someone."""
    has_swiped = await SwipeService.has_already_swiped(
        str(current_user.id),
        target_user_id
    )
    
    return {
        "has_swiped": has_swiped,
        "target_user_id": target_user_id
    }
