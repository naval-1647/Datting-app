from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class MessageBase(BaseModel):
    """Base message model."""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")


class MessageCreate(MessageBase):
    """Model for creating a message."""
    match_id: str = Field(..., description="Associated match ID")
    sender_id: str = Field(..., description="Sender's user ID")


class MessageUpdate(BaseModel):
    """Model for updating a message."""
    is_read: Optional[bool] = None


class MessageInDB(MessageBase):
    """Message model as stored in database."""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    match_id: str
    sender_id: str
    receiver_id: str  # Denormalized for easier queries
    is_read: bool = False
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class MessageResponse(MessageBase):
    """Message response model."""
    id: str = Field(..., alias="_id")
    match_id: str
    sender_id: str
    is_read: bool
    timestamp: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class MessageWithSender(MessageResponse):
    """Message response with sender profile info."""
    sender_name: Optional[str] = Field(None, description="Sender's name")
    sender_image: Optional[str] = Field(None, description="Sender's profile image")
