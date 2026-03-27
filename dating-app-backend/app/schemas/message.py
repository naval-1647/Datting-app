from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MessageCreate(BaseModel):
    """Message creation request."""
    content: str = Field(..., min_length=1, max_length=2000, description="Message content")


class MessageUpdate(BaseModel):
    """Message update request."""
    is_read: Optional[bool] = None


class MessageResponse(BaseModel):
    """Message response."""
    id: str = Field(..., alias="_id", description="Message ID")
    match_id: str = Field(..., description="Associated match ID")
    sender_id: str = Field(..., description="Sender user ID")
    content: str
    is_read: bool
    timestamp: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class MessageWithSender(MessageResponse):
    """Message with sender info."""
    sender_name: Optional[str] = Field(None, description="Sender's name")
    sender_image: Optional[str] = Field(None, description="Sender's profile image")


class ChatMessage(BaseModel):
    """WebSocket chat message."""
    type: str = Field(default="message", description="Message type: 'message', 'typing', 'read'")
    content: Optional[str] = Field(None, description="Message content")
    match_id: str = Field(..., description="Match ID")
    sender_id: str = Field(..., description="Sender user ID")
