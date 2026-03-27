from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class Token(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="Access token (short-lived)")
    refresh_token: str = Field(..., description="Refresh token (long-lived)")
    token_type: str = Field(default="bearer", description="Token type")


class TokenData(BaseModel):
    """Decoded token data."""
    user_id: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None  # "access" or "refresh"


class RefreshToken(BaseModel):
    """Refresh token request."""
    refresh_token: str = Field(..., description="Refresh token to get new access token")
