"""In-memory Notification Repository Implementation"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from app.repositories.interfaces.notification_repo import INotificationRepository
from app.db.models.notification import Notification


@dataclass
class NotificationData:
    """Internal data class for Notification"""
    id: UUID
    user_id: UUID
    title: str
    message: str
    is_read: bool = False
    type: str = "info"
    created_at: datetime = field(default_factory=datetime.utcnow)


class InMemoryNotificationRepository(INotificationRepository):
    """In-memory implementation of INotificationRepository"""
    
    def __init__(self):
        self._notifications: dict[UUID, NotificationData] = {}
    
    def _to_notification_model(self, data: NotificationData) -> Notification:
        """Convert internal data to Notification ORM model"""
        return Notification(
            id=data.id,
            user_id=data.user_id,
            title=data.title,
            message=data.message,
            is_read=data.is_read,
            type=data.type,
            created_at=data.created_at
        )
    
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID"""
        data = self._notifications.get(notification_id)
        return self._to_notification_model(data) if data else None
    
    async def get_by_user(self, user_id: UUID) -> List[Notification]:
        """Get all notifications for a user"""
        return [
            self._to_notification_model(data) 
            for data in self._notifications.values() 
            if data.user_id == user_id
        ]
    
    async def create(self, notification_data: dict) -> Notification:
        """Create new notification"""
        notification_id = uuid4()
        data = NotificationData(
            id=notification_id,
            user_id=notification_data["user_id"],
            title=notification_data["title"],
            message=notification_data["message"],
            type=notification_data.get("type", "info")
        )
        self._notifications[notification_id] = data
        return self._to_notification_model(data)
    
    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        """Mark notification as read"""
        data = self._notifications.get(notification_id)
        if not data:
            return None
        
        data.is_read = True
        return self._to_notification_model(data)
    
    async def mark_read(self, notification_id: UUID) -> Optional[Notification]:
        """Mark notification as read (alias for mark_as_read)"""
        return await self.mark_as_read(notification_id)
    
    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for user"""
        count = 0
        for data in self._notifications.values():
            if data.user_id == user_id and not data.is_read:
                data.is_read = True
                count += 1
        return count
    
    async def list_by_user(
        self, 
        user_id: UUID, 
        is_read: Optional[bool] = None
    ) -> List[Notification]:
        """List notifications by user with optional filter by is_read"""
        results = [
            self._to_notification_model(data) 
            for data in self._notifications.values() 
            if data.user_id == user_id
        ]
        
        if is_read is not None:
            results = [n for n in results if n.is_read == is_read]
        
        return results
    
    async def get_unread_count(self, user_id: UUID) -> int:
        """Get count of unread notifications for a user"""
        return sum(
            1 for data in self._notifications.values()
            if data.user_id == user_id and not data.is_read
        )
    
    async def delete(self, notification_id: UUID) -> bool:
        """Delete notification"""
        if notification_id in self._notifications:
            del self._notifications[notification_id]
            return True
        return False