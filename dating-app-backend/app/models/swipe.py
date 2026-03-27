from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId
from enum import Enum


class SwipeAction(str, Enum):
    """Swipe action types."""
    LIKE = "like"
    DISLIKE = "dislike"


class SwipeBase(BaseModel):
    """Base swipe model."""
    target_user_id: str = Field(..., description="ID of the user being swiped")
    action: SwipeAction = Field(..., description="Like or Dislike")


class SwipeCreate(SwipeBase):
    """Model for creating a swipe."""
    user_id: str = Field(..., description="ID of the user performing the swipe")


class SwipeInDB(SwipeBase):
    """Swipe model as stored in database."""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class SwipeResponse(SwipeBase):
    """Swipe response model."""
    id: str = Field(..., alias="_id")
    user_id: str
    created_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class SwipeWithProfile(SwipeResponse):
    """Swipe response with target user's profile info."""
    target_profile: Optional[dict] = Field(None, description="Target user's profile information")
