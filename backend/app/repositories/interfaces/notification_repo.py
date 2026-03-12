"""Notification Repository Interface"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.db.models.notification import Notification


class INotificationRepository(ABC):
    """Interface for Notification repository"""
    
    @abstractmethod
    async def create(self, notification_data: dict) -> Notification:
        """Create new notification"""
        pass
    
    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID"""
        pass
    
    @abstractmethod
    async def list_by_user(
        self, 
        user_id: UUID, 
        is_read: Optional[bool] = None
    ) -> List[Notification]:
        """List notifications by user"""
        pass
    
    @abstractmethod
    async def mark_read(self, notification_id: UUID) -> Optional[Notification]:
        """Mark notification as read"""
        pass
    
    @abstractmethod
    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for user"""
        pass
    
    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        """Get unread notification count for user"""
        pass