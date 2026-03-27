from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from app.database import db
from app.models.swipe import SwipeInDB, SwipeCreate, SwipeAction
from app.models.profile import Location

logger = logging.getLogger(__name__)


class SwipeService:
    """Swipe service for database operations and matching algorithm."""

    @staticmethod
    async def create_swipe(swipe_data: SwipeCreate) -> Optional[SwipeInDB]:
        """Create a swipe action."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Check for duplicate swipe
            existing_swipe = await database.swipes.find_one({
                "user_id": swipe_data.user_id,
                "target_user_id": swipe_data.target_user_id
            })
            
            if existing_swipe:
                logger.warning(f"Duplicate swipe detected: {swipe_data.user_id} -> {swipe_data.target_user_id}")
                return None

            # Create swipe document
            swipe_doc = swipe_data.model_dump()

            # Insert swipe
            result = await database.swipes.insert_one(swipe_doc)
            
            # Fetch created swipe
            swipe = await database.swipes.find_one({"_id": result.inserted_id})
            
            if swipe:
                return SwipeInDB(**swipe)
            return None

        except Exception as e:
            logger.error(f"Error creating swipe: {e}")
            raise

    @staticmethod
    async def check_match(user_id: str, target_user_id: str) -> bool:
        """Check if both users liked each other."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Check if current user liked target
            user_liked_target = await database.swipes.find_one({
                "user_id": user_id,
                "target_user_id": target_user_id,
                "action": SwipeAction.LIKE.value
            })

            # Check if target liked current user
            target_liked_user = await database.swipes.find_one({
                "user_id": target_user_id,
                "target_user_id": user_id,
                "action": SwipeAction.LIKE.value
            })

            is_match = user_liked_target is not None and target_liked_user is not None
            
            if is_match:
                logger.info(f"Match found between {user_id} and {target_user_id}")
            
            return is_match

        except Exception as e:
            logger.error(f"Error checking match: {e}")
            raise

    @staticmethod
    async def get_swipe_history(user_id: str, skip: int = 0, limit: int = 50) -> List[SwipeInDB]:
        """Get user's swipe history."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            swipes = await database.swipes.find(
                {"user_id": user_id}
            ).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
            
            return [SwipeInDB(**swipe) for swipe in swipes]

        except Exception as e:
            logger.error(f"Error getting swipe history: {e}")
            raise

    @staticmethod
    async def suggest_users(
        current_user_id: str,
        current_profile: Dict[str, Any],
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Suggest users based on location, age preference, interests.
        
        Uses MongoDB aggregation pipeline for efficient querying.
        """
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Get IDs of already swiped users
            swiped_users = await database.swipes.distinct(
                "target_user_id",
                {"user_id": current_user_id}
            )
            
            # Exclude self and already swiped users
            excluded_user_ids = [current_user_id] + swiped_users

            # Build aggregation pipeline
            pipeline = []

            # Stage 1: Match - filter out excluded users
            pipeline.append({
                "$match": {
                    "user_id": {"$nin": excluded_user_ids}
                }
            })

            # Stage 2: Geo proximity (if current user has location)
            if current_profile.get("location"):
                current_location = current_profile["location"]
                pipeline.append({
                    "$addFields": {
                        "distance": {
                            "$geoNear": {
                                "near": {
                                    "type": "Point",
                                    "coordinates": current_location.get("coordinates", [0, 0])
                                },
                                "distanceField": "distance",
                                "spherical": True
                            }
                        }
                    }
                })

            # Stage 3: Calculate match score
            pipeline.append({
                "$addFields": {
                    "match_score": {
                        "$add": [
                            # Proximity score (40%)
                            {"$cond": [{"$gt": ["$distance", 0]}, 
                                {"$multiply": [40, {"$divide": [100000, {"$add": ["$distance", 100000]}]}]},
                                20
                            ]},
                            # Common interests score (40%)
                            {"$multiply": [
                                40,
                                {"$divide": [
                                    {"$size": {"$setIntersection": [
                                        {"$ifNull": ["$interests", []]},
                                        current_profile.get("interests", [])
                                    ]}},
                                    {"$max": [1, {"$size": {"$ifNull": ["$interests", []]}}]}
                                ]}
                            ]},
                            # Activity bonus (20%) - recent activity
                            10
                        ]
                    }
                }
            })

            # Stage 4: Sort by match score
            pipeline.append({
                "$sort": {"match_score": -1}
            })

            # Stage 5: Limit results
            pipeline.append({
                "$limit": limit
            })

            # Execute aggregation
            suggested_profiles = await database.profiles.aggregate(pipeline).to_list(length=limit)

            # Enrich with distance
            results = []
            for profile in suggested_profiles:
                profile_dict = dict(profile)
                if "distance" in profile_dict:
                    profile_dict["distance_km"] = round(profile_dict["distance"] / 1000, 2)
                profile_dict["match_score"] = round(profile.get("match_score", 0), 2)
                results.append(profile_dict)

            logger.info(f"Suggested {len(results)} users for {current_user_id}")
            return results

        except Exception as e:
            logger.error(f"Error suggesting users: {e}")
            raise

    @staticmethod
    async def has_already_swiped(user_id: str, target_user_id: str) -> bool:
        """Check if user has already swiped on target."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            swipe = await database.swipes.find_one({
                "user_id": user_id,
                "target_user_id": target_user_id
            })
            
            return swipe is not None

        except Exception as e:
            logger.error(f"Error checking existing swipe: {e}")
            raise
