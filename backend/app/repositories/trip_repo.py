"""In-memory Trip Repository"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

from app.models.trip import Trip
from app.repositories.interfaces import ITripRepository


class InMemoryTripRepository(ITripRepository):
    """In-memory реализация TripRepository"""
    
    def __init__(self):
        self._trips: dict[UUID, Trip] = {}
    
    async def create(self, trip_data: dict) -> Trip:
        trip_id = uuid4()
        trip = Trip(
            id=trip_id,
            driver_id=trip_data["driver_id"],
            from_city=trip_data["from_city"],
            to_city=trip_data["to_city"],
            departure_date=trip_data["departure_date"],
            departure_time=trip_data["departure_time"],
            available_seats=trip_data["available_seats"],
            price_per_seat=trip_data["price_per_seat"],
            description=trip_data.get("description"),
            status=trip_data.get("status", "active"),
            created_at=datetime.utcnow()
        )
        self._trips[trip_id] = trip
        return trip
    
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        return self._trips.get(trip_id)
    
    async def update(self, trip_id: UUID, trip_data: dict) -> Optional[Trip]:
        if trip_id not in self._trips:
            return None
        trip = self._trips[trip_id]
        for key, value in trip_data.items():
            if hasattr(trip, key) and value is not None:
                setattr(trip, key, value)
        return trip
    
    async def delete(self, trip_id: UUID) -> bool:
        if trip_id not in self._trips:
            return False
        del self._trips[trip_id]
        return True
    
    async def list_by_filters(
        self,
        from_city: str,
        to_city: str,
        date: Optional[str] = None,
        status: str = "active"
    ) -> List[Trip]:
        results = []
        for trip in self._trips.values():
            # Normalize cities for comparison (case-insensitive)
            if (trip.from_city.lower() == from_city.lower() and
                trip.to_city.lower() == to_city.lower() and
                trip.status == status):
                if date is None or trip.departure_date == date:
                    results.append(trip)
        return results
    
    async def list_by_driver(self, driver_id: UUID) -> List[Trip]:
        return [
            trip for trip in self._trips.values()
            if trip.driver_id == driver_id
        ]
    
    async def update_seats(self, trip_id: UUID, seats_delta: int) -> Optional[Trip]:
        if trip_id not in self._trips:
            return None
        trip = self._trips[trip_id]
        trip.available_seats += seats_delta
        if trip.available_seats < 0:
            trip.available_seats = 0
        return trip
