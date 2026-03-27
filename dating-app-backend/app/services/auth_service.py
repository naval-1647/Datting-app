from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service for JWT and password management."""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password."""
        try:
            return bcrypt.checkpw(plain_password[:72].encode("utf-8"), hashed_password.encode("utf-8"))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password using bcrypt."""
        try:
            return bcrypt.hashpw(password[:72].encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        except Exception as e:
            logger.error(f"Password hashing error: {e}")
            raise

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

            to_encode.update({
                "exp": expire,
                "type": "access"
            })
            encoded_jwt = jwt.encode(
                to_encode,
                settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Access token creation error: {e}")
            raise

    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT refresh token."""
        try:
            to_encode = data.copy()
            if expires_delta:
                expire = datetime.now(timezone.utc) + expires_delta
            else:
                expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)

            to_encode.update({
                "exp": expire,
                "type": "refresh"
            })
            encoded_jwt = jwt.encode(
                to_encode,
                settings.jwt_secret_key,
                algorithm=settings.jwt_algorithm
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Refresh token creation error: {e}")
            raise

    @staticmethod
    def decode_token(token: str) -> Optional[dict]:
        """Decode and validate a JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            return payload
        except JWTError as e:
            logger.error(f"Token decoding error: {e}")
            return None
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return None

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[str]:
       
        payload = AuthService.decode_token(token)
        if payload is None:
            return None

        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None

        user_id = payload.get("sub")
        if user_id is None:
            return None

        return user_id
