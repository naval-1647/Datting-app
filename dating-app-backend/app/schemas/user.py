from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, max_length=100, description="User's password")


class UserCreate(BaseModel):
    """User signup request."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=6, max_length=100, description="User's password (min 6 chars)")


class UserUpdate(BaseModel):
    """User update request."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserResponse(BaseModel):
    """User response (excludes sensitive data)."""
    id: str = Field(..., alias="_id", description="User ID")
    email: EmailStr
    is_active: bool = True
    created_at: datetime

    class Config:
        populate_by_name = True
        from_attributes = True
