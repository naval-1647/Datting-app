from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from app.database import db
from app.models.match import MatchInDB, MatchCreate

logger = logging.getLogger(__name__)


class MatchService:
    """Match service for database operations."""

    @staticmethod
    async def create_match(user1_id: str, user2_id: str) -> Optional[MatchInDB]:
        """Create a new match."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Check if match already exists
            existing_match = await database.matches.find_one({
                "$or": [
                    {"user1_id": user1_id, "user2_id": user2_id},
                    {"user1_id": user2_id, "user2_id": user1_id}
                ]
            })
            
            if existing_match:
                logger.warning(f"Match already exists between {user1_id} and {user2_id}")
                return None

            # Ensure consistent ordering (smaller ID first)
            sorted_ids = sorted([user1_id, user2_id])
            
            # Create match document
            match_doc = {
                "user1_id": sorted_ids[0],
                "user2_id": sorted_ids[1],
                "created_at": datetime.now(timezone.utc),
                "matched_at": datetime.now(timezone.utc)
            }

            # Insert match
            result = await database.matches.insert_one(match_doc)
            
            # Fetch created match
            match = await database.matches.find_one({"_id": result.inserted_id})
            
            if match:
                logger.info(f"Match created: {sorted_ids[0]} <-> {sorted_ids[1]}")
                return MatchInDB(**match)
            return None

        except Exception as e:
            logger.error(f"Error creating match: {e}")
            raise

    @staticmethod
    async def get_user_matches(user_id: str, skip: int = 0, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all matches for a user with latest message info."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Find all matches where user is either user1 or user2
            matches = await database.matches.find({
                "$or": [
                    {"user1_id": user_id},
                    {"user2_id": user_id}
                ]
            }).sort("matched_at", -1).skip(skip).limit(limit).to_list(length=limit)

            # Enrich each match with profile and latest message
            enriched_matches = []
            for match in matches:
                match_dict = dict(match)
                
                # Get other user's ID
                other_user_id = match["user2_id"] if match["user1_id"] == user_id else match["user1_id"]
                
                # Get other user's profile
                other_profile = await database.profiles.find_one({"user_id": other_user_id})
                if other_profile:
                    match_dict["other_user_profile"] = {
                        "id": str(other_profile["_id"]),
                        "name": other_profile["name"],
                        "age": other_profile["age"],
                        "images": other_profile.get("images", [])
                    }
                
                # Get latest message
                latest_message = await database.messages.find_one(
                    {"match_id": str(match["_id"])},
                    sort=[("timestamp", -1)]
                )
                if latest_message:
                    match_dict["latest_message"] = latest_message["content"][:50]
                
                # Get unread count
                unread_count = await database.messages.count_documents({
                    "match_id": str(match["_id"]),
                    "sender_id": {"$ne": user_id},
                    "is_read": False
                })
                match_dict["unread_count"] = unread_count
                
                enriched_matches.append(match_dict)

            return enriched_matches

        except Exception as e:
            logger.error(f"Error getting user matches: {e}")
            raise

    @staticmethod
    async def get_match_by_id(match_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific match by ID."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            if not ObjectId.is_valid(match_id):
                return None
                
            match = await database.matches.find_one({"_id": ObjectId(match_id)})
            
            if match:
                return dict(match)
            return None

        except Exception as e:
            logger.error(f"Error getting match by ID: {e}")
            raise

    @staticmethod
    async def delete_match(match_id: str) -> bool:
        """Delete a match."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            if not ObjectId.is_valid(match_id):
                return False
            
            result = await database.matches.delete_one({"_id": ObjectId(match_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Match deleted: {match_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting match: {e}")
            raise

    @staticmethod
    async def check_match_exists(user1_id: str, user2_id: str) -> bool:
        """Check if a match exists between two users."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            match = await database.matches.find_one({
                "$or": [
                    {"user1_id": user1_id, "user2_id": user2_id},
                    {"user1_id": user2_id, "user2_id": user1_id}
                ]
            })
            
            return match is not None

        except Exception as e:
            logger.error(f"Error checking match existence: {e}")
            raise
