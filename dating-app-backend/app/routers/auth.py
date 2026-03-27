from fastapi import APIRouter, Depends, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
import logging

from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.services.profile_service import ProfileService
from app.models.user import UserInDB
from app.middleware import AuthenticationException, ValidationException, ConflictException
from app.dependencies import get_current_user
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate):
   
    try:
        # Create user
        user = await UserService.create_user(user_data)
        
        if not user:
            raise ConflictException("User with this email already exists")
        
        logger.info(f"New user registered: {user.email}")
        return user
        
    except ConflictException:
        raise
    except Exception as e:
        logger.error(f"Error during signup: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to create user account"
        )


@router.post("/login", response_model=Token)
async def login(login_data: UserLogin):
   
    try:
        # Get user by email
        user = await UserService.get_user_by_email(login_data.email)
        
        if not user:
            raise AuthenticationException("Invalid email or password")
        
        # Verify password
        if not AuthService.verify_password(login_data.password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")
        
        # Check if user is active
        if not user.is_active:
            raise AuthenticationException("Account is deactivated")
        
        # Create tokens
        access_token = AuthService.create_access_token(
            data={"sub": str(user.id)}
        )
        
        refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        logger.info(f"User logged in: {user.email}")
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
        
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed"
        )


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
   
    try:
        # Verify refresh token
        user_id = AuthService.verify_token(refresh_token, token_type="refresh")
        
        if not user_id:
            raise AuthenticationException("Invalid or expired refresh token")
        
        # Get user
        user = await UserService.get_user_by_id(user_id)
        
        if not user or not user.is_active:
            raise AuthenticationException("User not found or inactive")
        
        # Create new tokens
        new_access_token = AuthService.create_access_token(
            data={"sub": str(user.id)}
        )
        
        new_refresh_token = AuthService.create_refresh_token(
            data={"sub": str(user.id)}
        )
        
        logger.info(f"Token refreshed for user: {user.email}")
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer"
        }
        
    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(f"Error refreshing token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserInDB = Depends(get_current_user)):
   
    return current_user


@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_user)):
    """
    Logout current user (invalidate token on client side).
    
    **Note:** Since JWT is stateless, tokens need to be discarded on client side.
    For enhanced security, implement a token blacklist with Redis.
    
    **Headers:** Authorization: Bearer <access_token>
    """
    logger.info(f"User logged out: {current_user.email}")
    
    return {
        "success": True,
        "message": "Successfully logged out. Please discard your tokens."
    }
