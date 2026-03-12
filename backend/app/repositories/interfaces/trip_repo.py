"""Trip Repository Interface"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.db.models.trip import Trip


class ITripRepository(ABC):
    """Interface for Trip repository"""
    
    @abstractmethod
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """Get trip by ID"""
        pass
    
    @abstractmethod
    async def search(
        self, 
        from_city: str, 
        to_city: str, 
        date: Optional[str] = None, 
        status: str = "active"
    ) -> List[Trip]:
        """Search trips by filters"""
        pass
    
    @abstractmethod
    async def create(self, trip_data: dict) -> Trip:
        """Create new trip"""
        pass
    
    @abstractmethod
    async def update(self, trip_id: UUID, trip_data: dict) -> Optional[Trip]:
        """Update trip"""
        pass
    
    @abstractmethod
    async def delete(self, trip_id: UUID) -> bool:
        """Delete trip"""
        pass
    
    @abstractmethod
    async def list_by_driver(self, driver_id: UUID) -> List[Trip]:
        """List trips by driver"""
        pass
    
    @abstractmethod
    async def update_seats(self, trip_id: UUID, seats_delta: int) -> Optional[Trip]:
        """Update available seats (add/subtract)"""
        pass
    
    @abstractmethod
    async def lock_for_update(self, trip_id: UUID) -> Optional[Trip]:
        """Lock trip for update and return current state"""
        pass