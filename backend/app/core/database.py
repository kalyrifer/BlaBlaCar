"""
Инициализация in-memory storage.
"""
from app.repositories.inmemory.user_repo import InMemoryUserRepository
from app.repositories.inmemory.trip_repo import InMemoryTripRepository
from app.repositories.inmemory.request_repo import InMemoryRequestRepository
from app.repositories.inmemory.notification_repo import InMemoryNotificationRepository
from app.repositories.inmemory.refresh_token_repo import InMemoryRefreshTokenRepository


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
