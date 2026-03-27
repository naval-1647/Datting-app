from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import ASCENDING, TEXT
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager."""

    client: Optional[AsyncIOMotorClient] = None
    database: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect(cls):
        """Establish connection to MongoDB and create indexes."""
        try:
            cls.client = AsyncIOMotorClient(settings.mongodb_uri)
            cls.database = cls.client[settings.database_name]

            # Test connection
            await cls.client.admin.command("ping")
            logger.info(f"Connected to MongoDB: {settings.database_name}")

            # Create indexes for all collections
            await cls._create_indexes()

        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def _create_indexes(cls):
        """Create database indexes for optimal query performance."""
        db = cls.database

        # Users collection indexes
        await db.users.create_index([("email", ASCENDING)], unique=True)
        await db.users.create_index([("is_active", ASCENDING)])

        # Profiles collection indexes
        await db.profiles.create_index([("user_id", ASCENDING)], unique=True)
        await db.profiles.create_index([("location", "2dsphere")])  # Geo index
        await db.profiles.create_index([("age", ASCENDING)])
        await db.profiles.create_index([("gender", ASCENDING)])
        await db.profiles.create_index([("name", TEXT), ("bio", TEXT)])  # Full-text search
        await db.profiles.create_index([("interests", ASCENDING)])

        # Swipes collection indexes
        await db.swipes.create_index(
            [("user_id", ASCENDING), ("target_user_id", ASCENDING)],
            unique=True
        )
        await db.swipes.create_index([("user_id", ASCENDING)])
        await db.swipes.create_index([("target_user_id", ASCENDING)])
        await db.swipes.create_index([("action", ASCENDING)])

        # Matches collection indexes
        await db.matches.create_index([("user1_id", ASCENDING)])
        await db.matches.create_index([("user2_id", ASCENDING)])
        await db.matches.create_index(
            [("user1_id", ASCENDING), ("user2_id", ASCENDING)],
            unique=True
        )
        await db.matches.create_index([("created_at", ASCENDING)])

        # Messages collection indexes
        await db.messages.create_index([("match_id", ASCENDING)])
        await db.messages.create_index([("sender_id", ASCENDING)])
        await db.messages.create_index([("timestamp", ASCENDING)])
        await db.messages.create_index([("match_id", ASCENDING), ("timestamp", ASCENDING)])

        # Notifications collection indexes
        await db.notifications.create_index([("user_id", ASCENDING)])
        await db.notifications.create_index([("is_read", ASCENDING)])
        await db.notifications.create_index([("created_at", ASCENDING)])

        logger.info("Database indexes created successfully")

    @classmethod
    async def disconnect(cls):
        """Close MongoDB connection."""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")


# Global database instance
db = Database()
