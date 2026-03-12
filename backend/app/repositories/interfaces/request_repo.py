"""Request Repository Interface"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.db.models.trip_request import TripRequest


class IRequestRepository(ABC):
    """Interface for Trip Request repository"""
    
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[TripRequest]:
        """Get request by ID"""
        pass
    
    @abstractmethod
    async def create(self, request_data: dict) -> TripRequest:
        """Create new request"""
        pass
    
    @abstractmethod
    async def update_status(self, request_id: UUID, status: str) -> Optional[TripRequest]:
        """Update request status"""
        pass
    
    @abstractmethod
    async def list_by_trip(self, trip_id: UUID) -> List[TripRequest]:
        """List requests by trip"""
        pass
    
    @abstractmethod
    async def list_by_passenger(self, passenger_id: UUID) -> List[TripRequest]:
        """List requests by passenger"""
        pass
    
    @abstractmethod
    async def exists(self, trip_id: UUID, passenger_id: UUID) -> bool:
        """Check if request exists for trip and passenger"""
        pass