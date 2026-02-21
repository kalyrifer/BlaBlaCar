"""
Инициализация in-memory storage.
"""
from app.repositories.user_repo import InMemoryUserRepository
from app.repositories.trip_repo import InMemoryTripRepository
from app.repositories.request_repo import InMemoryRequestRepository
from app.repositories.notification_repo import InMemoryNotificationRepository


class Database:
    """Database container for in-memory repositories"""
    
    def __init__(self):
        self.users = InMemoryUserRepository()
        self.trips = InMemoryTripRepository()
        self.requests = InMemoryRequestRepository()
        self.notifications = InMemoryNotificationRepository()


# Singleton instance
db = Database()


def get_db() -> Database:
    """Get database instance"""
    return db
