"""Notification backend adapters - Pluggable architecture for different notification backends"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from uuid import UUID
import logging

from app.repositories.interfaces import INotificationRepository

logger = logging.getLogger(__name__)


class NotificationBackend(ABC):
    """
    Abstract interface for notification backends.
    Implement this to add support for different notification systems.
    """
    
    @abstractmethod
    async def send_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send a notification to a user.
        
        Args:
            user_id: UUID of the recipient
            title: Notification title
            message: Notification message body
            notification_type: Type of notification (e.g., "request_status", "trip_update")
            metadata: Additional metadata for the notification
            
        Returns:
            True if notification was sent successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend (e.g., establish connections)"""
        pass
    
    @abstractmethod
    async def shutdown(self) -> None:
        """Shutdown the backend (e.g., close connections)"""
        pass


class InProcessAdapter(NotificationBackend):
    """
    In-process notification adapter.
    Saves notifications to the repository and simulates sending (logs).
    """
    
    def __init__(self, notification_repo: INotificationRepository):
        """
        Initialize the in-process adapter.
        
        Args:
            notification_repo: Repository for persisting notifications
        """
        self._notification_repo = notification_repo
        logger.info("InProcessAdapter initialized")
    
    async def initialize(self) -> None:
        """Initialize the adapter"""
        logger.info("InProcessAdapter: Initialized")
    
    async def shutdown(self) -> None:
        """Shutdown the adapter"""
        logger.info("InProcessAdapter: Shutdown")
    
    async def send_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Send notification via in-process adapter.
        Saves to repository and logs the notification.
        
        Args:
            user_id: UUID of the recipient
            title: Notification title
            message: Notification message body
            notification_type: Type of notification
            metadata: Additional metadata
            
        Returns:
            True if notification was processed successfully
        """
        try:
            # Create notification record in repository
            notification_data = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "notification_type": notification_type,
                "is_read": False,
                "metadata": metadata or {}
            }
            
            await self._notification_repo.create(notification_data)
            
            # Simulate sending - in production, this would send email/push/etc.
            logger.info(
                f"[InProcessAdapter] Notification sent to user {user_id}: "
                f"[{notification_type}] {title} - {message}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send in-process notification: {e}")
            return False


class CeleryAdapter(NotificationBackend):
    """
    Celery-based notification adapter (for future implementation).
    
    This adapter can be used when you want to delegate notification
    processing to a Celery worker for background processing.
    
    Example usage:
        from celery import shared_task
        
        @shared_task
        def send_notification_task(user_id, title, message, ...):
            # Celery task implementation
            pass
    """
    
    def __init__(self, task_name: str = "app.background.tasks.send_notification"):
        """
        Initialize the Celery adapter.
        
        Args:
            task_name: Name of the Celery task to invoke
        """
        self._task_name = task_name
        logger.info(f"CeleryAdapter initialized with task: {task_name}")
    
    async def initialize(self) -> None:
        """Initialize the Celery connection"""
        logger.info("CeleryAdapter: Initialized")
        # In production: self._celery_app = Celery(...)
    
    async def shutdown(self) -> None:
        """Shutdown the Celery connection"""
        logger.info("CeleryAdapter: Shutdown")
        # In production: self._celery_app = None
    
    async def send_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Queue notification for Celery worker processing.
        
        Args:
            user_id: UUID of the recipient
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            metadata: Additional metadata
            
        Returns:
            True if task was queued successfully
        """
        try:
            # In production:
            # from app.celery_app import celery_app
            # celery_app.send_task(
            #     self._task_name,
            #     args=[str(user_id), title, message, notification_type],
            #     kwargs={"metadata": metadata}
            # )
            
            logger.info(
                f"[CeleryAdapter] Notification queued for user {user_id}: "
                f"[{notification_type}] {title}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to queue Celery notification: {e}")
            return False


class RedisAdapter(NotificationBackend):
    """
    Redis-based notification adapter (for future implementation).
    
    This adapter can be used with Redis Pub/Sub or Redis lists
    for real-time notification delivery.
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """
        Initialize the Redis adapter.
        
        Args:
            redis_url: Redis connection URL
        """
        self._redis_url = redis_url
        self._redis_client = None
        logger.info(f"RedisAdapter initialized with URL: {redis_url}")
    
    async def initialize(self) -> None:
        """Initialize the Redis connection"""
        logger.info("RedisAdapter: Initialized")
        # In production:
        # import redis
        # self._redis_client = redis.from_url(self._redis_url)
    
    async def shutdown(self) -> None:
        """Shutdown the Redis connection"""
        logger.info("RedisAdapter: Shutdown")
        # In production:
        # if self._redis_client:
        #     self._redis_client.close()
    
    async def send_notification(
        self,
        user_id: UUID,
        title: str,
        message: str,
        notification_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Push notification to Redis for real-time delivery.
        
        Args:
            user_id: UUID of the recipient
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            metadata: Additional metadata
            
        Returns:
            True if notification was pushed successfully
        """
        try:
            # In production:
            # import json
            # notification = {
            #     "user_id": str(user_id),
            #     "title": title,
            #     "message": message,
            #     "type": notification_type,
            #     "metadata": metadata
            # }
            # channel = f"notifications:{user_id}"
            # self._redis_client.publish(channel, json.dumps(notification))
            
            logger.info(
                f"[RedisAdapter] Notification pushed for user {user_id}: "
                f"[{notification_type}] {title}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to push Redis notification: {e}")
            return False


# Factory function to get the appropriate adapter
def get_notification_backend(
    backend_type: str = "in_process",
    notification_repo: Optional[INotificationRepository] = None
) -> NotificationBackend:
    """
    Factory function to create notification backends.
    
    Args:
        backend_type: Type of backend ("in_process", "celery", "redis")
        notification_repo: Required for in_process adapter
        
    Returns:
        NotificationBackend instance
    """
    if backend_type == "in_process":
        if not notification_repo:
            raise ValueError("notification_repo required for in_process adapter")
        return InProcessAdapter(notification_repo)
    elif backend_type == "celery":
        return CeleryAdapter()
    elif backend_type == "redis":
        return RedisAdapter()
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")
