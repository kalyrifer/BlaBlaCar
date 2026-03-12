"""Background tasks module - notification worker and adapters"""
from app.background.worker import (
    enqueue_notification,
    get_notification_queue,
    notification_worker,
    wait_for_queue_drain,
    set_notification_backend,
    get_notification_backend
)
from app.background.adapters import (
    NotificationBackend,
    InProcessAdapter,
    CeleryAdapter,
    RedisAdapter,
    get_notification_backend as get_backend
)

__all__ = [
    # Worker functions
    "enqueue_notification",
    "get_notification_queue", 
    "notification_worker",
    "wait_for_queue_drain",
    "set_notification_backend",
    "get_notification_backend",
    # Adapters
    "NotificationBackend",
    "InProcessAdapter", 
    "CeleryAdapter",
    "RedisAdapter",
    "get_backend"
]
