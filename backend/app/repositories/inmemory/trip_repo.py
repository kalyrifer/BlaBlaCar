"""In-memory Trip Repository Implementation with locking"""
from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    departure_at: datetime
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str = "active"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = None


class InMemoryTripRepository(ITripRepository):
    """In-memory implementation of ITripRepository with locking"""
    
    def __init__(self):
        self._trips: dict[UUID, TripData] = {}
        self._lock_manager = get_lock_manager()
    
    def _to_trip_model(self, data: TripData) -> Trip:
        """Convert internal data to Trip ORM model"""
        # Ensure departure_at is timezone-aware UTC
        departure_at = data.departure_at
        if departure_at.tzinfo is None:
            departure_at = departure_at.replace(tzinfo=timezone.utc)
        
        return Trip(
            id=data.id,
            driver_id=data.driver_id,
            from_city=data.from_city,
            to_city=data.to_city,
            departure_at=departure_at,
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
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: str = "active"
    ) -> List[Trip]:
        """Search trips by filters"""
        results = []
        for data in self._trips.values():
            if (data.from_city == from_city and 
                data.to_city == to_city and
                data.status == status):
                
                # Date range filtering
                departure_at = data.departure_at
                if departure_at.tzinfo is None:
                    departure_at = departure_at.replace(tzinfo=timezone.utc)
                
                if date_from is not None:
                    # Compare with timezone-aware datetime
                    if departure_at < date_from:
                        continue
                
                if date_to is not None:
                    # Compare with timezone-aware datetime
                    if departure_at > date_to:
                        continue
                
                results.append(self._to_trip_model(data))
        return results
    
    async def create(self, trip_data: dict) -> Trip:
        """Create new trip"""
        # Handle departure_at - ensure it's timezone-aware UTC
        departure_at = trip_data.get("departure_at")
        if departure_at is None:
            raise ValueError("departure_at is required")
        
        if isinstance(departure_at, str):
            # Parse string to datetime
            departure_at = datetime.fromisoformat(departure_at.replace('Z', '+00:00'))
        
        if departure_at.tzinfo is None:
            departure_at = departure_at.replace(tzinfo=timezone.utc)
        else:
            departure_at = departure_at.astimezone(timezone.utc)
        
        # Use provided ID if present, otherwise generate new one
        trip_id = trip_data.get("id") or uuid4()
        data = TripData(
            id=trip_id,
            driver_id=trip_data["driver_id"],
            from_city=trip_data["from_city"],
            to_city=trip_data["to_city"],
            departure_at=departure_at,
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
        
        # Handle departure_at update
        if "departure_at" in trip_data:
            departure_at = trip_data["departure_at"]
            if isinstance(departure_at, str):
                departure_at = datetime.fromisoformat(departure_at.replace('Z', '+00:00'))
            if departure_at.tzinfo is None:
                departure_at = departure_at.replace(tzinfo=timezone.utc)
            else:
                departure_at = departure_at.astimezone(timezone.utc)
            trip_data["departure_at"] = departure_at
        
        for key, value in trip_data.items():
            if hasattr(data, key):
                setattr(data, key, value)
        
        data.updated_at = datetime.now(timezone.utc)
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
            data.updated_at = datetime.now(timezone.utc)
            return self._to_trip_model(data)
    
    async def lock_for_update(self, trip_id: UUID) -> Optional[Trip]:
        """Lock trip for update and return current state"""
        async with self._lock_manager.lock_for("trip", str(trip_id)):
            data = self._trips.get(trip_id)
            return self._to_trip_model(data) if data else None
