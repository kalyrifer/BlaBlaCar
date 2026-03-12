"""Background worker for processing notifications asynchronously"""
import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

from app.background.adapters import NotificationBackend, InProcessAdapter

logger = logging.getLogger(__name__)

# Global notification queue
_notification_queue: asyncio.Queue[Dict[str, Any]] = None

# Global notification backend adapter
_notification_backend: Optional[NotificationBackend] = None


def get_notification_queue() -> asyncio.Queue:
    """Get the global notification queue"""
    global _notification_queue
    if _notification_queue is None:
        _notification_queue = asyncio.Queue()
    return _notification_queue


def set_notification_backend(backend: NotificationBackend) -> None:
    """Set the global notification backend adapter"""
    global _notification_backend
    _notification_backend = backend


def get_notification_backend() -> Optional[NotificationBackend]:
    """Get the global notification backend adapter"""
    return _notification_backend


def enqueue_notification(notification_payload: Dict[str, Any]) -> None:
    """
    Enqueue a notification for async processing.
    
    Args:
        notification_payload: Dictionary containing notification data:
            - user_id: UUID of the recipient
            - title: Notification title
            - message: Notification message
            - notification_type: Type of notification (e.g., "request_status", "trip_update")
    """
    queue = get_notification_queue()
    # Add timestamp for processing
    payload = {
        **notification_payload,
        "queued_at": datetime.utcnow()
    }
    queue.put_nowait(payload)
    logger.info(f"Notification enqueued for user {notification_payload.get('user_id')}")


async def notification_worker(
    notification_queue: asyncio.Queue,
    process_callback: Any = None
) -> None:
    """
    Worker coroutine that processes notifications from the queue.
    
    Args:
        notification_queue: The queue to consume notifications from
        process_callback: Optional callback for custom processing
    """
    logger.info("Notification worker started")
    backend = get_notification_backend()
    
    while True:
        try:
            # Get notification from queue with timeout to allow graceful shutdown
            notification = await asyncio.wait_for(
                notification_queue.get(),
                timeout=1.0
            )
            
            logger.info(f"Processing notification: {notification.get('title')}")
            
            try:
                if process_callback:
                    # Use custom callback if provided
                    await process_callback(notification)
                elif backend:
                    # Use the configured backend adapter
                    await backend.send_notification(
                        user_id=notification.get("user_id"),
                        title=notification.get("title", ""),
                        message=notification.get("message", ""),
                        notification_type=notification.get("notification_type", "general"),
                        metadata=notification.get("metadata")
                    )
                else:
                    # Default processing - just log
                    logger.info(
                        f"Default processing: Would send notification to user "
                        f"{notification.get('user_id')}: {notification.get('title')}"
                    )
                    
            except Exception as e:
                logger.error(f"Error processing notification: {e}")
                # In production, implement retry logic or dead letter queue
                
            finally:
                notification_queue.task_done()
                
        except asyncio.TimeoutError:
            # No item available, continue loop
            continue
        except asyncio.CancelledError:
            logger.info("Notification worker cancelled")
            break
        except Exception as e:
            logger.error(f"Unexpected error in notification worker: {e}")
            
    logger.info("Notification worker stopped")


async def wait_for_queue_drain(notification_queue: asyncio.Queue, timeout: float = 5.0) -> bool:
    """
    Wait for the queue to be drained within the timeout period.
    
    Args:
        notification_queue: The queue to wait on
        timeout: Maximum time to wait in seconds
        
    Returns:
        True if queue is empty, False if timeout
    """
    try:
        await asyncio.wait_for(notification_queue.join(), timeout=timeout)
        return True
    except asyncio.TimeoutError:
        return False
