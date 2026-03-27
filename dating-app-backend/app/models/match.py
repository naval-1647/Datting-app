from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class MatchBase(BaseModel):
    """Base match model."""
    pass


class MatchCreate(BaseModel):
    """Model for creating a match."""
    user1_id: str = Field(..., description="First user ID")
    user2_id: str = Field(..., description="Second user ID")


class MatchInDB(MatchBase):
    """Match model as stored in database."""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user1_id: str
    user2_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    matched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class MatchResponse(MatchBase):
    """Match response model."""
    id: str = Field(..., alias="_id")
    user1_id: str
    user2_id: str
    created_at: datetime
    matched_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class MatchWithProfile(MatchResponse):
    """Match response with the other user's profile."""
    other_user_profile: Optional[dict] = Field(None, description="Other user's profile information")
    latest_message: Optional[str] = Field(None, description="Latest message preview")
    unread_count: int = Field(0, description="Number of unread messages")
