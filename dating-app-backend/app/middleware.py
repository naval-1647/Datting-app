from fastapi import FastAPI, Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Callable
import logging

from app.config import settings

logger = logging.getLogger(__name__)


def setup_rate_limiter(app: FastAPI) -> Limiter:
    """Setup rate limiter for the application."""
    
    # Create limiter instance
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=[f"{settings.rate_limit_per_minute}/minute"]
    )
    
    # Initialize app with limiter
    app.state.limiter = limiter
    
    return limiter


def login_rate_limit() -> str:
    """Rate limit decorator for login endpoint."""
    return f"{settings.login_rate_limit_per_minute}/minute"


def swipe_rate_limit() -> str:
    """Rate limit decorator for swipe endpoints."""
    return "100/hour"


async def ip_ban_middleware(request: Request, call_next):
    """Middleware to check for banned IPs (placeholder for future implementation)."""
    # TODO: Implement IP ban logic
    return await call_next(request)


async def request_logging_middleware(request: Request, call_next):
    """Log all incoming requests."""
    logger.info(f"{request.method} {request.url.path}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


class AppException(Exception):
    """Base exception for custom app exceptions."""
    def __init__(
        self,
        message: str,
        code: str = "UNKNOWN_ERROR",
        status_code: int = 500
    ):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(self.message)


class ValidationException(AppException):
    """Validation error exception."""
    def __init__(self, message: str, details: dict = None):
        super().__init__(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400
        )
        self.details = details or {}


class AuthenticationException(AppException):
    """Authentication error exception."""
    def __init__(self, message: str = "Invalid authentication credentials"):
        super().__init__(
            message=message,
            code="AUTHENTICATION_ERROR",
            status_code=401
        )


class AuthorizationException(AppException):
    """Authorization error exception."""
    def __init__(self, message: str = "Not authorized to perform this action"):
        super().__init__(
            message=message,
            code="AUTHORIZATION_ERROR",
            status_code=403
        )


class NotFoundException(AppException):
    """Resource not found exception."""
    def __init__(self, message: str = "Resource not found"):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404
        )


class ConflictException(AppException):
    """Conflict exception (e.g., duplicate resource)."""
    def __init__(self, message: str = "Resource conflict"):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409
        )
