from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SwipeAction(str, Enum):
    """Swipe action types."""
    LIKE = "like"
    DISLIKE = "dislike"


class SwipeCreate(BaseModel):
    """Swipe creation request."""
    target_user_id: str = Field(..., description="ID of user to swipe")
    action: SwipeAction = Field(..., description="Like or Dislike")


class SwipeResponse(BaseModel):
    """Swipe response."""
    id: str = Field(..., alias="_id", description="Swipe ID")
    user_id: str = Field(..., description="User who performed swipe")
    target_user_id: str = Field(..., description="Swiped user ID")
    action: SwipeAction
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class SwipeWithProfile(SwipeResponse):
    """Swipe with target profile info."""
    target_profile: Optional[dict] = Field(None, description="Target user's profile")
