from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List
import logging

from app.database import db
from app.models.profile import ProfileInDB, ProfileCreate, ProfileUpdate

logger = logging.getLogger(__name__)


class ProfileService:
    """Profile service for database operations."""

    @staticmethod
    async def create_profile(profile_data: ProfileCreate) -> Optional[ProfileInDB]:
        """Create a new profile in the database."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Check if profile already exists for user
            existing_profile = await database.profiles.find_one({"user_id": profile_data.user_id})
            if existing_profile:
                logger.warning(f"Profile already exists for user {profile_data.user_id}")
                return None

            # Create profile document
            profile_doc = profile_data.model_dump()

            # Insert profile
            result = await database.profiles.insert_one(profile_doc)
            
            # Fetch created profile
            profile = await database.profiles.find_one({"_id": result.inserted_id})
            
            if profile:
                return ProfileInDB(**profile)
            return None

        except Exception as e:
            logger.error(f"Error creating profile: {e}")
            raise

    @staticmethod
    async def get_profile_by_user_id(user_id: str) -> Optional[ProfileInDB]:
        """Get a profile by user ID."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            profile = await database.profiles.find_one({"user_id": user_id})
            
            if profile:
                return ProfileInDB(**profile)
            return None

        except Exception as e:
            logger.error(f"Error getting profile by user ID: {e}")
            raise

    @staticmethod
    async def get_profile_by_id(profile_id: str) -> Optional[ProfileInDB]:
        """Get a profile by profile ID."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            if not ObjectId.is_valid(profile_id):
                return None
                
            profile = await database.profiles.find_one({"_id": ObjectId(profile_id)})
            
            if profile:
                return ProfileInDB(**profile)
            return None

        except Exception as e:
            logger.error(f"Error getting profile by ID: {e}")
            raise

    @staticmethod
    async def update_profile(user_id: str, profile_update: ProfileUpdate) -> Optional[ProfileInDB]:
        """Update a profile."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            update_data = profile_update.model_dump(exclude_unset=True)
            
            if not update_data:
                return await ProfileService.get_profile_by_user_id(user_id)

            result = await database.profiles.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )

            if result.modified_count > 0 or result.matched_count > 0:
                return await ProfileService.get_profile_by_user_id(user_id)
            return None

        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            raise

    @staticmethod
    async def add_profile_image(user_id: str, image_url: str) -> Optional[ProfileInDB]:
        """Add an image to a profile."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            result = await database.profiles.update_one(
                {"user_id": user_id},
                {"$push": {"images": image_url}}
            )

            if result.modified_count > 0 or result.matched_count > 0:
                return await ProfileService.get_profile_by_user_id(user_id)
            return None

        except Exception as e:
            logger.error(f"Error adding profile image: {e}")
            raise

    @staticmethod
    async def remove_profile_image(user_id: str, image_url: str) -> Optional[ProfileInDB]:
        """Remove an image from a profile."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            result = await database.profiles.update_one(
                {"user_id": user_id},
                {"$pull": {"images": image_url}}
            )

            if result.modified_count > 0 or result.matched_count > 0:
                return await ProfileService.get_profile_by_user_id(user_id)
            return None

        except Exception as e:
            logger.error(f"Error removing profile image: {e}")
            raise

    @staticmethod
    async def search_profiles(
        query: Optional[str] = None,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
        gender: Optional[str] = None,
        interests: Optional[List[str]] = None,
        location: Optional[List[float]] = None,
        radius_km: Optional[float] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[ProfileInDB]:
        """Search profiles with filters."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Build query
            filter_query = {}

            if age_min is not None or age_max is not None:
                filter_query["age"] = {}
                if age_min is not None:
                    filter_query["age"]["$gte"] = age_min
                if age_max is not None:
                    filter_query["age"]["$lte"] = age_max

            if gender:
                filter_query["gender"] = gender

            if interests:
                filter_query["interests"] = {"$in": interests}

            if location and radius_km:
                filter_query["location"] = {
                    "$near": {
                        "$geometry": {
                            "type": "Point",
                            "coordinates": location
                        },
                        "$maxDistance": radius_km * 1000  # Convert to meters
                    }
                }

            # Text search if query provided
            if query:
                text_search = await database.profiles.find(
                    {"$text": {"$search": query}},
                    {"score": {"$meta": "textScore"}}
                ).sort([("score", {"$meta": "textScore"})]).skip(skip).limit(limit).to_list(length=limit)
                return [ProfileInDB(**profile) for profile in text_search]

            # Regular search
            profiles = await database.profiles.find(filter_query).skip(skip).limit(limit).to_list(length=limit)
            
            return [ProfileInDB(**profile) for profile in profiles]

        except Exception as e:
            logger.error(f"Error searching profiles: {e}")
            raise
