"""In-memory Trip Repository Implementation with locking"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from app.repositories.interfaces.trip_repo import ITripRepository
from app.db.models.trip import Trip
from app.repositories.inmemory.locks import get_lock_manager


@dataclass
class TripData:
    """Internal data class for Trip"""
    id: UUID
    driver_id: UUID
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class InMemoryTripRepository(ITripRepository):
    """In-memory implementation of ITripRepository with locking"""
    
    def __init__(self):
        self._trips: dict[UUID, TripData] = {}
        self._lock_manager = get_lock_manager()
    
    def _to_trip_model(self, data: TripData) -> Trip:
        """Convert internal data to Trip ORM model"""
        return Trip(
            id=data.id,
            driver_id=data.driver_id,
            from_city=data.from_city,
            to_city=data.to_city,
            departure_date=data.departure_date,
            departure_time=data.departure_time,
            available_seats=data.available_seats,
            price_per_seat=data.price_per_seat,
            description=data.description,
            status=data.status,
            created_at=data.created_at
        )
    
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """Get trip by ID"""
        data = self._trips.get(trip_id)
        return self._to_trip_model(data) if data else None
    
    async def search(
        self, 
        from_city: str, 
        to_city: str, 
        date: Optional[str] = None, 
        status: str = "active"
    ) -> List[Trip]:
        """Search trips by filters"""
        results = []
        for data in self._trips.values():
            if (data.from_city == from_city and 
                data.to_city == to_city and
                data.status == status):
                if date is None or data.departure_date == date:
                    results.append(self._to_trip_model(data))
        return results
    
    async def create(self, trip_data: dict) -> Trip:
        """Create new trip"""
        # Use provided ID if present, otherwise generate new one
        trip_id = trip_data.get("id") or uuid4()
        data = TripData(
            id=trip_id,
            driver_id=trip_data["driver_id"],
            from_city=trip_data["from_city"],
            to_city=trip_data["to_city"],
            departure_date=trip_data["departure_date"],
            departure_time=trip_data["departure_time"],
            available_seats=trip_data["available_seats"],
            price_per_seat=trip_data["price_per_seat"],
            description=trip_data.get("description"),
            status=trip_data.get("status", "active")
        )
        self._trips[trip_id] = data
        return self._to_trip_model(data)
    
    async def update(self, trip_id: UUID, trip_data: dict) -> Optional[Trip]:
        """Update trip"""
        data = self._trips.get(trip_id)
        if not data:
            return None
        
        for key, value in trip_data.items():
            if hasattr(data, key):
                setattr(data, key, value)
        
        data.updated_at = datetime.utcnow()
        return self._to_trip_model(data)
    
    async def delete(self, trip_id: UUID) -> bool:
        """Delete trip"""
        if trip_id in self._trips:
            del self._trips[trip_id]
            return True
        return False
    
    async def list_by_driver(self, driver_id: UUID) -> List[Trip]:
        """List trips by driver"""
        return [
            self._to_trip_model(data) 
            for data in self._trips.values() 
            if data.driver_id == driver_id
        ]
    
    async def update_seats(self, trip_id: UUID, seats_delta: int) -> Optional[Trip]:
        """Update available seats (add/subtract) - atomic operation with lock"""
        async with self._lock_manager.lock_for("trip", str(trip_id)):
            data = self._trips.get(trip_id)
            if not data:
                return None
            
            new_seats = data.available_seats + seats_delta
            if new_seats < 0:
                raise ValueError("Not enough available seats")
            
            data.available_seats = new_seats
            data.updated_at = datetime.utcnow()
            return self._to_trip_model(data)
    
    async def lock_for_update(self, trip_id: UUID) -> Optional[Trip]:
        """Lock trip for update and return current state"""
        async with self._lock_manager.lock_for("trip", str(trip_id)):
            data = self._trips.get(trip_id)
            return self._to_trip_model(data) if data else None