from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class Location(BaseModel):
    """GeoJSON location."""
    type: str = Field(default="Point")
    coordinates: List[float] = Field(..., min_length=2, max_length=2)  # [longitude, latitude]


class ProfileCreate(BaseModel):
    """Profile creation request."""
    name: str = Field(..., min_length=1, max_length=100, description="Display name")
    age: int = Field(..., ge=18, le=120, description="Age (must be 18+)")
    gender: str = Field(..., description="Gender")
    bio: Optional[str] = Field(None, max_length=500, description="Short bio")
    interests: List[str] = Field(default_factory=list, description="Interests")
    location: Location = Field(..., description="Location for proximity matching")


class ProfileUpdate(BaseModel):
    """Profile update request."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=18, le=120)
    gender: Optional[str] = None
    bio: Optional[str] = Field(None, max_length=500)
    interests: Optional[List[str]] = None
    location: Optional[Location] = None


class ProfileResponse(BaseModel):
    """Profile response."""
    id: str = Field(..., alias="_id", description="Profile ID")
    user_id: str = Field(..., description="Associated user ID")
    name: str
    age: int
    gender: str
    bio: Optional[str] = None
    interests: List[str] = []
    location: Location
    images: List[str] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True


class ProfileWithDistance(ProfileResponse):
    """Profile with distance and match score."""
    distance_km: Optional[float] = Field(None, description="Distance in kilometers")
    match_score: Optional[float] = Field(None, description="Compatibility score (0-100)")
