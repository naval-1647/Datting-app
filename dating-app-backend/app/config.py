from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # MongoDB Configuration
    mongodb_uri: str = "mongodb://localhost:27017"
    database_name: str = "dating_app"

    # JWT Configuration
    jwt_secret_key: str = "your-super-secret-jwt-key-change-this-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7

    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8000"
    cors_allow_credentials: bool = True

    # Cloudinary Configuration
    cloudinary_cloud_name: str = ""
    cloudinary_api_key: str = ""
    cloudinary_api_secret: str = ""

    # Storage Configuration
    storage_type: str = "local"  # 'local' or 'cloudinary'
    local_storage_path: str = "./uploads"

    # Security
    secret_key: str = "your-secret-key-for-password-hashing-change-this-in-production"

    # Rate Limiting
    rate_limit_per_minute: int = 100
    login_rate_limit_per_minute: int = 5

    # Application Settings
    debug: bool = True
    api_prefix: str = "/api/v1"
    project_name: str = "Dating App API"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
