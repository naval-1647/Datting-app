from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MatchResponse(BaseModel):
    """Match response."""
    id: str = Field(..., alias="_id", description="Match ID")
    user1_id: str = Field(..., description="First user ID")
    user2_id: str = Field(..., description="Second user ID")
    created_at: datetime
    matched_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class MatchWithProfile(MatchResponse):
    """Match with other user's profile."""
    other_user_profile: Optional[dict] = Field(None, description="Other user's profile")
    latest_message: Optional[str] = Field(None, description="Latest message preview")
    unread_count: int = Field(0, description="Unread message count")
