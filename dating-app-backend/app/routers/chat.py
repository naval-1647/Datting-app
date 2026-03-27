from fastapi import APIRouter, Depends, HTTPException, status, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
from datetime import datetime

from app.schemas.message import MessageCreate, MessageResponse, ChatMessage
from app.services.message_service import MessageService
from app.services.match_service import MatchService
from app.services.notification_service import NotificationService
from app.websocket import manager
from app.models.user import UserInDB
from app.dependencies import get_current_user
from app.middleware import NotFoundException, ValidationException
from app.database import db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/{match_id}")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    match_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """WebSocket endpoint for real-time chat."""
    try:
        # Verify match exists and user is part of it
        match = await MatchService.get_match_by_id(match_id)
        
        if not match:
            await websocket.close(code=4004, reason="Match not found")
            return
        
        if match["user1_id"] != str(current_user.id) and match["user2_id"] != str(current_user.id):
            await websocket.close(code=4003, reason="Not authorized")
            return
        
        # Connect to WebSocket
        await manager.connect(websocket, str(current_user.id))
        manager.add_to_match(match_id, str(current_user.id))
        
        # Send online status to other participant
        other_user_id = match["user2_id"] if match["user1_id"] == str(current_user.id) else match["user1_id"]
        
        await manager.send_personal_message({
            "type": "status",
            "data": {
                "user_id": str(current_user.id),
                "status": "online"
            }
        }, other_user_id)
        
        try:
            while True:
                # Receive message
                data = await websocket.receive_json()
                
                message_type = data.get("type", "message")
                
                if message_type == "message":
                    # Save message to database
                    content = data.get("content", "").strip()
                    
                    if not content:
                        continue
                    
                    message_data = MessageCreate(
                        match_id=match_id,
                        sender_id=str(current_user.id),
                        content=content
                    )
                    
                    # Get receiver ID
                    receiver_id = other_user_id
                    
                    saved_message = await MessageService.create_message(
                        message_data,
                        receiver_id
                    )
                    
                    if saved_message:
                        # Broadcast to other user
                        await manager.broadcast_to_match({
                            "type": "message",
                            "data": {
                                "id": str(saved_message.id),
                                "match_id": match_id,
                                "sender_id": str(current_user.id),
                                "content": content,
                                "timestamp": saved_message.timestamp.isoformat(),
                                "is_read": False
                            }
                        }, match_id, exclude_user=str(current_user.id))
                        
                        # Send notification if recipient is offline
                        if not manager.is_user_online(receiver_id):
                            await NotificationService.create_notification(
                                receiver_id,
                                "new_message",
                                {
                                    "match_id": match_id,
                                    "sender_id": str(current_user.id),
                                    "content": content[:100]
                                }
                            )
                
                elif message_type == "typing":
                    # Send typing indicator
                    await manager.broadcast_to_match({
                        "type": "typing",
                        "data": {
                            "user_id": str(current_user.id),
                            "match_id": match_id
                        }
                    }, match_id, exclude_user=str(current_user.id))
                
                elif message_type == "read":
                    # Mark messages as read
                    await MessageService.mark_messages_as_read(match_id, str(current_user.id))
                    
                    # Notify other user
                    await manager.broadcast_to_match({
                        "type": "read",
                        "data": {
                            "user_id": str(current_user.id),
                            "match_id": match_id
                        }
                    }, match_id, exclude_user=str(current_user.id))
        
        except WebSocketDisconnect:
            manager.disconnect(str(current_user.id))
            manager.remove_from_match(match_id, str(current_user.id))
            
            # Notify other user about offline status
            await manager.send_personal_message({
                "type": "status",
                "data": {
                    "user_id": str(current_user.id),
                    "status": "offline"
                }
            }, other_user_id)
            
            logger.info(f"User {current_user.id} disconnected from chat")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        try:
            await websocket.close(code=4000, reason="Connection error")
        except:
            pass


@router.get("/{match_id}/history", response_model=list[MessageResponse])
async def get_message_history(
    match_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """Get message history for a match (REST fallback)."""
    # Verify match exists
    match = await MatchService.get_match_by_id(match_id)
    
    if not match:
        raise NotFoundException("Match not found")
    
    # Verify user is part of match
    if match["user1_id"] != str(current_user.id) and match["user2_id"] != str(current_user.id):
        raise NotFoundException("Match not found")
    
    messages = await MessageService.get_message_history(match_id, skip, limit)
    
    return messages


@router.post("/{match_id}/messages", response_model=MessageResponse)
async def send_message(
    match_id: str,
    message_data: MessageCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Send a message via REST API (fallback if WebSocket not available)."""
    # Verify match exists
    match = await MatchService.get_match_by_id(match_id)
    
    if not match:
        raise NotFoundException("Match not found")
    
    # Verify user is part of match
    if match["user1_id"] != str(current_user.id) and match["user2_id"] != str(current_user.id):
        raise NotFoundException("Not authorized to send messages in this match")
    
    # Get receiver ID
    receiver_id = match["user2_id"] if match["user1_id"] == str(current_user.id) else match["user1_id"]
    
    # Save message
    message_data.match_id = match_id
    message_data.sender_id = str(current_user.id)
    
    saved_message = await MessageService.create_message(message_data, receiver_id)
    
    if not saved_message:
        raise HTTPException(status_code=500, detail="Failed to send message")
    
    # Send notification if recipient is offline
    if not manager.is_user_online(receiver_id):
        await NotificationService.create_notification(
            receiver_id,
            "new_message",
            {
                "match_id": match_id,
                "sender_id": str(current_user.id),
                "content": saved_message.content[:100]
            }
        )
    
    return saved_message


@router.post("/{match_id}/read")
async def mark_messages_read(
    match_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Mark all messages as read in a match."""
    count = await MessageService.mark_messages_as_read(match_id, str(current_user.id))
    
    return {
        "success": True,
        "marked_count": count
    }
