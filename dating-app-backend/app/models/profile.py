from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime, timezone
from bson import ObjectId


class Location(BaseModel):
    """GeoJSON location for proximity queries."""
    type: Literal["Point"] = Field(default="Point")
    coordinates: List[float] = Field(..., min_length=2, max_length=2)  # [longitude, latitude]


class ProfileBase(BaseModel):
    """Base profile model."""
    name: str = Field(..., min_length=1, max_length=100, description="User's display name")
    age: int = Field(..., ge=18, le=120, description="User's age (must be 18+)")
    gender: str = Field(..., description="User's gender")
    bio: Optional[str] = Field(None, max_length=500, description="Short bio")
    interests: List[str] = Field(default_factory=list, description="List of interests")
    location: Location = Field(..., description="User's location for proximity matching")


class ProfileCreate(ProfileBase):
    """Model for creating a profile."""
    user_id: str = Field(..., description="Associated user ID")


class ProfileUpdate(BaseModel):
    """Model for updating a profile."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    interests: Optional[List[str]] = None
    location: Optional[Location] = None


class ProfileInDB(ProfileBase):
    """Profile model as stored in database."""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    images: List[str] = Field(default_factory=list, description="Profile image URLs")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class ProfileResponse(ProfileBase):
    """Profile response model."""
    id: str = Field(..., alias="_id")
    user_id: str
    images: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            ObjectId: str
        }


class ProfileWithDistance(ProfileResponse):
    """Profile response with distance information."""
    distance_km: Optional[float] = Field(None, description="Distance from current user in km")
    match_score: Optional[float] = Field(None, description="Compatibility score (0-100)")
