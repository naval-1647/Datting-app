from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from app.database import db
from app.models.message import MessageInDB, MessageCreate

logger = logging.getLogger(__name__)


class MessageService:
    """Message service for database operations."""

    @staticmethod
    async def create_message(message_data: MessageCreate, receiver_id: str) -> Optional[MessageInDB]:
        """Create a new message."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Create message document
            message_doc = {
                "match_id": message_data.match_id,
                "sender_id": message_data.sender_id,
                "receiver_id": receiver_id,
                "content": message_data.content,
                "is_read": False,
                "timestamp": datetime.now(timezone.utc)
            }

            # Insert message
            result = await database.messages.insert_one(message_doc)
            
            # Fetch created message
            message = await database.messages.find_one({"_id": result.inserted_id})
            
            if message:
                logger.info(f"Message created: {message_data.sender_id} -> {receiver_id}")
                return MessageInDB(**message)
            return None

        except Exception as e:
            logger.error(f"Error creating message: {e}")
            raise

    @staticmethod
    async def get_message_history(
        match_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> List[MessageInDB]:
        """Get message history for a match."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            messages = await database.messages.find(
                {"match_id": match_id}
            ).sort("timestamp", -1).skip(skip).limit(limit).to_list(length=limit)
            
            # Reverse to show oldest first
            messages.reverse()
            
            return [MessageInDB(**msg) for msg in messages]

        except Exception as e:
            logger.error(f"Error getting message history: {e}")
            raise

    @staticmethod
    async def mark_messages_as_read(match_id: str, user_id: str) -> int:
        """Mark all messages from other user as read."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            result = await database.messages.update_many(
                {
                    "match_id": match_id,
                    "sender_id": {"$ne": user_id},
                    "is_read": False
                },
                {"$set": {"is_read": True}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Marked {result.modified_count} messages as read for user {user_id}")
            
            return result.modified_count

        except Exception as e:
            logger.error(f"Error marking messages as read: {e}")
            raise

    @staticmethod
    async def get_unread_count(match_id: str, user_id: str) -> int:
        """Get count of unread messages for a user in a match."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            count = await database.messages.count_documents({
                "match_id": match_id,
                "sender_id": {"$ne": user_id},
                "is_read": False
            })
            
            return count

        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            raise

    @staticmethod
    async def delete_message(message_id: str) -> bool:
        """Delete a message."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            if not ObjectId.is_valid(message_id):
                return False
            
            result = await database.messages.delete_one({"_id": ObjectId(message_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Message deleted: {message_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting message: {e}")
            raise

    @staticmethod
    async def get_latest_message(match_id: str) -> Optional[MessageInDB]:
        """Get the latest message in a match."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            message = await database.messages.find_one(
                {"match_id": match_id},
                sort=[("timestamp", -1)]
            )
            
            if message:
                return MessageInDB(**message)
            return None

        except Exception as e:
            logger.error(f"Error getting latest message: {e}")
            raise
