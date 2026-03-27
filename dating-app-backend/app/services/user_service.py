from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
from datetime import datetime, timezone
import logging

from app.database import db
from app.models.user import UserInDB, UserCreate, UserUpdate
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)


class UserService:
    """User service for database operations."""

    @staticmethod
    async def create_user(user_data: UserCreate) -> Optional[UserInDB]:
        """Create a new user in the database."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Check if user already exists
            existing_user = await database.users.find_one({"email": user_data.email})
            if existing_user:
                logger.warning(f"User with email {user_data.email} already exists")
                return None

            # Hash password
            hashed_password = AuthService.get_password_hash(user_data.password)

            # Create user document
            user_doc = {
                "email": user_data.email,
                "hashed_password": hashed_password,
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }

            # Insert user
            result = await database.users.insert_one(user_doc)
            
            # Fetch created user
            user = await database.users.find_one({"_id": result.inserted_id})
            
            if user:
                return UserInDB.model_validate(user)
            return None

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            raise

    @staticmethod
    async def get_user_by_id(user_id: str) -> Optional[UserInDB]:
        """Get a user by ID."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            if not ObjectId.is_valid(user_id):
                return None
                
            user = await database.users.find_one({"_id": ObjectId(user_id)})
            
            if user:
                return UserInDB.model_validate(user)
            return None

        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            raise

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[UserInDB]:
        """Get a user by email."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            user = await database.users.find_one({"email": email})
            
            if user:
                return UserInDB.model_validate(user)
            return None

        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            raise

    @staticmethod
    async def update_user(user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        """Update a user."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            update_data = user_update.model_dump(exclude_unset=True)
            
            if not update_data:
                return await UserService.get_user_by_id(user_id)

            # Hash password if being updated
            if "password" in update_data:
                update_data["hashed_password"] = AuthService.get_password_hash(update_data.pop("password"))

            result = await database.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )

            if result.modified_count > 0 or result.matched_count > 0:
                return await UserService.get_user_by_id(user_id)
            return None

        except Exception as e:
            logger.error(f"Error updating user: {e}")
            raise

    @staticmethod
    async def delete_user(user_id: str) -> bool:
        """Delete a user."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            result = await database.users.delete_one({"_id": ObjectId(user_id)})
            
            return result.deleted_count > 0

        except Exception as e:
            logger.error(f"Error deleting user: {e}")
            raise

    @staticmethod
    async def get_all_users(skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """Get all users with pagination."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            users = await database.users.find().skip(skip).limit(limit).to_list(length=limit)
            
            return [UserInDB.model_validate(user) for user in users]

        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            raise
