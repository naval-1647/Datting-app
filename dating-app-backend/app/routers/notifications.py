from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging

from app.services.notification_service import NotificationService
from app.models.user import UserInDB
from app.dependencies import get_current_user
from app.middleware import NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/")
async def get_notifications(
    unread_only: bool = False,
    current_user: UserInDB = Depends(get_current_user)
):
    """Get all notifications for current user."""
    notifications = await NotificationService.get_user_notifications(
        str(current_user.id),
        unread_only=unread_only
    )
    
    return notifications


@router.get("/unread-count")
async def get_unread_count(
    current_user: UserInDB = Depends(get_current_user)
):
    """Get count of unread notifications."""
    count = await NotificationService.get_unread_count(str(current_user.id))
    
    return {"unread_count": count}


@router.put("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Mark a notification as read."""
    success = await NotificationService.mark_as_read(notification_id)
    
    if not success:
        raise NotFoundException("Notification not found")
    
    return {"success": True, "message": "Notification marked as read"}


@router.put("/read-all")
async def mark_all_read(
    current_user: UserInDB = Depends(get_current_user)
):
    """Mark all notifications as read."""
    count = await NotificationService.mark_all_as_read(str(current_user.id))
    
    return {
        "success": True,
        "marked_count": count
    }


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Delete a notification."""
    success = await NotificationService.delete_notification(notification_id)
    
    if not success:
        raise NotFoundException("Notification not found")
    
    return {"success": True, "message": "Notification deleted"}
