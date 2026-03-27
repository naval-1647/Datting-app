from fastapi import WebSocket
from typing import Dict, List, Optional
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket connection manager for real-time chat."""

    def __init__(self):
        # Store active connections: user_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Store match connections: match_id -> set of user_ids
        self.match_participants: Dict[str, set] = defaultdict(set)
        
        # Store online status: user_id -> bool
        self.online_status: Dict[str, bool] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept WebSocket connection for a user."""
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.online_status[user_id] = True
        logger.info(f"User {user_id} connected via WebSocket")

    def disconnect(self, user_id: str):
        """Disconnect a user's WebSocket connection."""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        self.online_status[user_id] = False
        
        # Clean up match participants
        for match_id, participants in self.match_participants.items():
            if user_id in participants:
                participants.discard(user_id)
        
        logger.info(f"User {user_id} disconnected from WebSocket")

    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to a specific user."""
        if user_id in self.active_connections:
            try:
                await self.active_connections[user_id].send_json(message)
                logger.debug(f"Message sent to user {user_id}: {message.get('type')}")
            except Exception as e:
                logger.error(f"Error sending message to user {user_id}: {e}")
                self.disconnect(user_id)
        else:
            logger.warning(f"User {user_id} not connected, cannot send message")

    async def broadcast_to_match(self, message: dict, match_id: str, exclude_user: Optional[str] = None):
        """Broadcast a message to all users in a match."""
        if match_id in self.match_participants:
            for user_id in self.match_participants[match_id]:
                if user_id != exclude_user:
                    await self.send_personal_message(message, user_id)

    def add_to_match(self, match_id: str, user_id: str):
        """Add a user to a match room."""
        self.match_participants[match_id].add(user_id)
        logger.info(f"User {user_id} added to match {match_id}")

    def remove_from_match(self, match_id: str, user_id: str):
        """Remove a user from a match room."""
        if match_id in self.match_participants:
            self.match_participants[match_id].discard(user_id)
            logger.info(f"User {user_id} removed from match {match_id}")

    def is_user_online(self, user_id: str) -> bool:
        """Check if a user is online."""
        return self.online_status.get(user_id, False)

    def get_online_users_in_match(self, match_id: str) -> List[str]:
        """Get list of online users in a match."""
        if match_id not in self.match_participants:
            return []
        
        return [
            user_id for user_id in self.match_participants[match_id]
            if self.is_user_online(user_id)
        ]


# Global connection manager instance
manager = ConnectionManager()
