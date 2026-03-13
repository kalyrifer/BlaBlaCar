"""
Инициализация in-memory storage.
"""
from app.repositories.inmemory.user_repo import InMemoryUserRepository
from app.repositories.inmemory.trip_repo import InMemoryTripRepository
from app.repositories.inmemory.request_repo import InMemoryRequestRepository
from app.repositories.inmemory.notification_repo import InMemoryNotificationRepository
from app.repositories.inmemory.refresh_token_repo import InMemoryRefreshTokenRepository
from app.repositories.interfaces import IUserRepository, ITripRepository, IRequestRepository, INotificationRepository, IRefreshTokenRepository


class Database:
    """Database container for in-memory repositories"""
    
    def __init__(self):
        self.users = InMemoryUserRepository()
        self.trips = InMemoryTripRepository()
        self.requests = InMemoryRequestRepository()
        self.notifications = InMemoryNotificationRepository()
        self.refresh_tokens = InMemoryRefreshTokenRepository()


# Singleton instance
db = Database()


def get_db() -> Database:
    """Get database instance"""
    return db


def get_user_repo() -> IUserRepository:
    """Get user repository"""
    return db.users


def get_trip_repo() -> ITripRepository:
    """Get trip repository"""
    return db.trips


def get_request_repo() -> IRequestRepository:
    """Get request repository"""
    return db.requests


def get_notification_repo() -> INotificationRepository:
    """Get notification repository"""
    return db.notifications


def get_refresh_token_repo() -> IRefreshTokenRepository:
    """Get refresh token repository"""
    return db.refresh_tokens
