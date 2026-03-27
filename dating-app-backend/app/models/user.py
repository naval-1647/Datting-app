from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime, timezone
from bson import ObjectId


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic."""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v, handler):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema):
        field_schema.update(type="string")


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr = Field(..., description="User's email address")


class UserCreate(UserBase):
    """Model for creating a new user."""
    password: str = Field(..., min_length=6, max_length=100, description="User's password")


class UserUpdate(BaseModel):
    """Model for updating user."""
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class UserInDB(UserBase):
    """User model as stored in database."""
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    hashed_password: str
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "populate_by_name": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if isinstance(obj, dict) and "_id" in obj and not isinstance(obj["_id"], str):
            obj = {**obj, "_id": str(obj["_id"])}
        return super().model_validate(obj, *args, **kwargs)


class UserResponse(UserBase):
    """User response model (excludes sensitive data)."""
    id: str = Field(..., alias="_id")
    is_active: bool
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "json_encoders": {datetime: lambda v: v.isoformat()},
    }

    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        if isinstance(obj, dict) and "_id" in obj and not isinstance(obj["_id"], str):
            obj = {**obj, "_id": str(obj["_id"])}
        return super().model_validate(obj, *args, **kwargs)
