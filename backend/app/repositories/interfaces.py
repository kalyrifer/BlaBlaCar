"""Интерфейсы Repository (Abstract Base Classes)"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.models.user import User
from app.models.trip import Trip
from app.models.request import TripRequest
from app.models.notification import Notification


class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def create(self, user_data: dict) -> User:
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
    
    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def list_all(self) -> List[User]:
        pass


class ITripRepository(ABC):
    """Интерфейс репозитория поездок"""
    
    @abstractmethod
    async def create(self, trip_data: dict) -> Trip:
        pass
    
    @abstractmethod
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        pass
    
    @abstractmethod
    async def update(self, trip_id: UUID, trip_data: dict) -> Optional[Trip]:
        pass
    
    @abstractmethod
    async def delete(self, trip_id: UUID) -> bool:
        pass
    
    @abstractmethod
    async def list_by_filters(
        self, 
        from_city: str, 
        to_city: str, 
        date: Optional[str] = None, 
        status: str = "active"
    ) -> List[Trip]:
        pass
    
    @abstractmethod
    async def list_by_driver(self, driver_id: UUID) -> List[Trip]:
        pass
    
    @abstractmethod
    async def update_seats(self, trip_id: UUID, seats_delta: int) -> Optional[Trip]:
        pass


class IRequestRepository(ABC):
    """Интерфейс репозитория заявок"""
    
    @abstractmethod
    async def create(self, request_data: dict) -> TripRequest:
        pass
    
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[TripRequest]:
        pass
    
    @abstractmethod
    async def get_by_trip(self, trip_id: UUID) -> List[TripRequest]:
        pass
    
    @abstractmethod
    async def get_by_passenger(self, passenger_id: UUID) -> List[TripRequest]:
        pass
    
    @abstractmethod
    async def update_status(self, request_id: UUID, status: str) -> Optional[TripRequest]:
        pass
    
    @abstractmethod
    async def exists(self, trip_id: UUID, passenger_id: UUID) -> bool:
        pass


class INotificationRepository(ABC):
    """Интерфейс репозитория уведомлений"""
    
    @abstractmethod
    async def create(self, notification_data: dict) -> Notification:
        pass
    
    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        pass
    
    @abstractmethod
    async def get_by_user(
        self, 
        user_id: UUID, 
        is_read: Optional[bool] = None
    ) -> List[Notification]:
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        pass
    
    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int:
        pass
    
    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        pass
