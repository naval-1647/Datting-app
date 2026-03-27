from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import UserInDB
from app.middleware import AuthenticationException, ValidationException

logger = logging.getLogger(__name__)


# HTTP Bearer token security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> UserInDB:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Authorization header with Bearer token
        
    Returns:
        Current authenticated user
        
    Raises:
        AuthenticationException: If token is invalid or user not found
    """
    try:
        token = credentials.credentials
        
        # Verify token and get user_id
        user_id = AuthService.verify_token(token, token_type="access")
        
        if not user_id:
            raise AuthenticationException("Invalid or expired token")
        
        # Get user from database
        user = await UserService.get_user_by_id(user_id)
        
        if not user:
            raise AuthenticationException("User not found")
        
        if not user.is_active:
            raise AuthenticationException("User account is inactive")
        
        return user
        
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Error getting current user: {e}")
        raise AuthenticationException("Authentication failed")


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[UserInDB]:
    """
    Dependency to optionally get current user (doesn't fail if no token).
    
    Useful for endpoints that work differently for authenticated vs anonymous users.
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        user_id = AuthService.verify_token(token, token_type="access")
        
        if not user_id:
            return None
        
        user = await UserService.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            return None
        
        return user
        
    except Exception:
        return None


def rate_limit_decorator(limit_string: str):
    """Decorator for applying rate limits to endpoints."""
    def decorator(func):
        func._rate_limit = limit_string
        return func
    return decorator


async def validate_user_profile_exists(user: UserInDB = Depends(get_current_user)):
    """Validate that the user has a profile created."""
    from app.services.profile_service import ProfileService
    
    profile = await ProfileService.get_profile_by_user_id(str(user.id))
    
    if not profile:
        raise ValidationException(
            message="Profile not found. Please create your profile first.",
            details={"user_id": str(user.id)}
        )
    
    return user, profile
