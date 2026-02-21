"""In-memory Notification Repository"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

from app.models.notification import Notification
from app.repositories.interfaces import INotificationRepository


class InMemoryNotificationRepository(INotificationRepository):
    """In-memory реализация NotificationRepository"""
    
    def __init__(self):
        self._notifications: dict[UUID, Notification] = {}
    
    async def create(self, notification_data: dict) -> Notification:
        notification_id = uuid4()
        notification = Notification(
            id=notification_id,
            user_id=notification_data["user_id"],
            type=notification_data["type"],
            title=notification_data["title"],
            message=notification_data["message"],
            is_read=notification_data.get("is_read", False),
            related_trip_id=notification_data.get("related_trip_id"),
            related_request_id=notification_data.get("related_request_id"),
            created_at=datetime.utcnow()
        )
        self._notifications[notification_id] = notification
        return notification
    
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        return self._notifications.get(notification_id)
    
    async def get_by_user(
        self,
        user_id: UUID,
        is_read: Optional[bool] = None
    ) -> List[Notification]:
        results = [
            notif for notif in self._notifications.values()
            if notif.user_id == user_id
        ]
        if is_read is not None:
            results = [n for n in results if n.is_read == is_read]
        return sorted(results, key=lambda x: x.created_at, reverse=True)
    
    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        if notification_id not in self._notifications:
            return None
        notification = self._notifications[notification_id]
        notification.is_read = True
        return notification
    
    async def mark_all_as_read(self, user_id: UUID) -> int:
        count = 0
        for notif in self._notifications.values():
            if notif.user_id == user_id and not notif.is_read:
                notif.is_read = True
                count += 1
        return count
    
    async def get_unread_count(self, user_id: UUID) -> int:
        return sum(
            1 for notif in self._notifications.values()
            if notif.user_id == user_id and not notif.is_read
        )
