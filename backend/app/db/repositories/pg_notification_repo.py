"""PostgreSQL Notification Repository using SQLAlchemy"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

from app.db.models.notification import Notification
from app.repositories.interfaces.notification_repo import INotificationRepository


class PGNotificationRepository(INotificationRepository):
    """PostgreSQL implementation of INotificationRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, notification_data: dict) -> Notification:
        """Create new notification"""
        notification = Notification(**notification_data)
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification
    
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Get notification by ID"""
        stmt = select(Notification).where(Notification.id == notification_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_by_user(
        self, 
        user_id: UUID, 
        is_read: Optional[bool] = None
    ) -> List[Notification]:
        """List notifications by user"""
        stmt = select(Notification).where(Notification.user_id == user_id)
        
        if is_read is not None:
            stmt = stmt.where(Notification.is_read == is_read)
        
        stmt = stmt.order_by(Notification.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def mark_read(self, notification_id: UUID) -> Optional[Notification]:
        """Mark notification as read"""
        notification = await self.get_by_id(notification_id)
        if notification is None:
            return None
        
        notification.is_read = True
        await self.session.commit()
        await self.session.refresh(notification)
        return notification
    
    async def mark_all_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for user"""
        stmt = (
            update(Notification)
            .where(Notification.user_id == user_id)
            .values(is_read=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
    
    async def get_unread_count(self, user_id: UUID) -> int:
        """Get unread notification count for user"""
        stmt = (
            select(func.count(Notification.id))
            .where(Notification.user_id == user_id)
            .where(Notification.is_read == False)
        )
        result = await self.session.execute(stmt)
        return result.scalar() or 0
