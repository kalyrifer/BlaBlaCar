"""Repository interfaces package"""
from app.repositories.interfaces.user_repo import IUserRepository
from app.repositories.interfaces.trip_repo import ITripRepository
from app.repositories.interfaces.request_repo import IRequestRepository
from app.repositories.interfaces.notification_repo import INotificationRepository
from app.repositories.interfaces.refresh_token_repo import IRefreshTokenRepository

__all__ = [
    "IUserRepository",
    "ITripRepository",
    "IRequestRepository",
    "INotificationRepository",
    "IRefreshTokenRepository",
]