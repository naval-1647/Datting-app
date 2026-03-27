from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import logging

from app.database import db

logger = logging.getLogger(__name__)


class NotificationService:
    """Notification service for database operations."""

    @staticmethod
    async def create_notification(
        user_id: str,
        notification_type: str,
        data: Dict[str, Any],
        title: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Create a new notification."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            # Create notification document
            notification_doc = {
                "user_id": user_id,
                "type": notification_type,
                "title": title or NotificationService._get_default_title(notification_type),
                "data": data,
                "is_read": False,
                "created_at": datetime.now(timezone.utc)
            }

            # Insert notification
            result = await database.notifications.insert_one(notification_doc)
            
            # Fetch created notification
            notification = await database.notifications.find_one({"_id": result.inserted_id})
            
            if notification:
                notification_dict = dict(notification)
                notification_dict["id"] = str(notification_dict.pop("_id"))
                logger.info(f"Notification created for user {user_id}: {notification_type}")
                return notification_dict
            return None

        except Exception as e:
            logger.error(f"Error creating notification: {e}")
            raise

    @staticmethod
    def _get_default_title(notification_type: str) -> str:
        """Get default title for notification type."""
        titles = {
            "new_match": "New Match!",
            "new_message": "New Message",
            "profile_view": "Someone viewed your profile"
        }
        return titles.get(notification_type, "Notification")

    @staticmethod
    async def get_user_notifications(
        user_id: str,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get notifications for a user."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            query = {"user_id": user_id}
            if unread_only:
                query["is_read"] = False

            notifications = await database.notifications.find(query).sort(
                "created_at", -1
            ).skip(skip).limit(limit).to_list(length=limit)

            # Convert ObjectId to string and _id to id
            result = []
            for notif in notifications:
                notif_dict = dict(notif)
                notif_dict["id"] = str(notif_dict.pop("_id"))
                result.append(notif_dict)

            return result

        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            raise

    @staticmethod
    async def mark_as_read(notification_id: str) -> bool:
        """Mark a notification as read."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            if not ObjectId.is_valid(notification_id):
                return False
            
            result = await database.notifications.update_one(
                {"_id": ObjectId(notification_id)},
                {"$set": {"is_read": True}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Notification marked as read: {notification_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")
            raise

    @staticmethod
    async def mark_all_as_read(user_id: str) -> int:
        """Mark all notifications as read for a user."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            result = await database.notifications.update_many(
                {"user_id": user_id, "is_read": False},
                {"$set": {"is_read": True}}
            )
            
            if result.modified_count > 0:
                logger.info(f"Marked {result.modified_count} notifications as read for user {user_id}")
            
            return result.modified_count

        except Exception as e:
            logger.error(f"Error marking all notifications as read: {e}")
            raise

    @staticmethod
    async def delete_notification(notification_id: str) -> bool:
        """Delete a notification."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            if not ObjectId.is_valid(notification_id):
                return False
            
            result = await database.notifications.delete_one({"_id": ObjectId(notification_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Notification deleted: {notification_id}")
                return True
            return False

        except Exception as e:
            logger.error(f"Error deleting notification: {e}")
            raise

    @staticmethod
    async def get_unread_count(user_id: str) -> int:
        """Get count of unread notifications."""
        try:
            database: AsyncIOMotorDatabase = db.database
            
            count = await database.notifications.count_documents({
                "user_id": user_id,
                "is_read": False
            })
            
            return count

        except Exception as e:
            logger.error(f"Error getting unread count: {e}")
            raise
