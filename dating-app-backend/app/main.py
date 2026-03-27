from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from app.config import settings
from app.database import db
from app.routers import auth, users, profiles, swipes, matches, chat, notifications
from app.middleware import setup_rate_limiter, AppException

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.debug else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


# Custom exception handler for rate limiting
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": f"Too many requests. Please try again later.",
                "details": str(exc)
            }
        }
    )


def create_application() -> FastAPI:
    """Create and configure FastAPI application."""
    
    application = FastAPI(
        title=settings.project_name,
        description="Production-ready Dating App Backend with real-time chat, matching algorithm, and JWT authentication",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )

    # Setup CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Setup rate limiter
    limiter = setup_rate_limiter(application)

    # Add rate limit exception handler
    application.add_exception_handler(RateLimitExceeded, rate_limit_handler)

    # Add custom app exception handler
    @application.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"success": False, "error": {"code": exc.code, "message": exc.message}}
        )

    # Include routers
    api_prefix = settings.api_prefix
    
    application.include_router(auth.router, prefix=f"{api_prefix}/auth", tags=["Authentication"])
    application.include_router(users.router, prefix=f"{api_prefix}/users", tags=["Users"])
    application.include_router(profiles.router, prefix=f"{api_prefix}/profiles", tags=["Profiles"])
    application.include_router(swipes.router, prefix=f"{api_prefix}/swipes", tags=["Swipes"])
    application.include_router(matches.router, prefix=f"{api_prefix}/matches", tags=["Matches"])
    application.include_router(chat.router, prefix=f"{api_prefix}/chat", tags=["Chat"])
    application.include_router(notifications.router, prefix=f"{api_prefix}/notifications", tags=["Notifications"])

    @application.on_event("startup")
    async def startup_db_client():
        """Connect to database on startup."""
        logger.info("Starting up Dating App API...")
        await db.connect()
        logger.info("Database connection established")

    @application.on_event("shutdown")
    async def shutdown_db_client():
        """Disconnect from database on shutdown."""
        logger.info("Shutting down Dating App API...")
        await db.disconnect()
        logger.info("Database connection closed")

    @application.get("/")
    async def root():
        """Root endpoint - API health check."""
        return {
            "success": True,
            "data": {
                "name": settings.project_name,
                "version": "1.0.0",
                "status": "running",
                "docs": "/docs"
            }
        }

    @application.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "database": "connected" if db.client else "disconnected"
            }
        }

    return application


# Create application instance
app = create_application()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
