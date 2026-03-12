"""In-memory Request Repository Implementation"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from app.repositories.interfaces.request_repo import IRequestRepository
from app.db.models.trip_request import TripRequest


@dataclass
class RequestData:
    """Internal data class for TripRequest"""
    id: UUID
    trip_id: UUID
    passenger_id: UUID
    seats: int
    status: str
    message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class InMemoryRequestRepository(IRequestRepository):
    """In-memory implementation of IRequestRepository"""
    
    def __init__(self):
        self._requests: dict[UUID, RequestData] = {}
    
    def _to_request_model(self, data: RequestData) -> TripRequest:
        """Convert internal data to TripRequest ORM model"""
        return TripRequest(
            id=data.id,
            trip_id=data.trip_id,
            passenger_id=data.passenger_id,
            seats_requested=data.seats,
            status=data.status,
            message=data.message,
            created_at=data.created_at
        )
    
    async def get_by_id(self, request_id: UUID) -> Optional[TripRequest]:
        """Get request by ID"""
        data = self._requests.get(request_id)
        return self._to_request_model(data) if data else None
    
    async def get_by_trip(self, trip_id: UUID) -> List[TripRequest]:
        """Get all requests for a trip"""
        return [
            self._to_request_model(data) 
            for data in self._requests.values() 
            if data.trip_id == trip_id
        ]
    
    async def get_by_passenger(self, passenger_id: UUID) -> List[TripRequest]:
        """Get all requests by passenger"""
        return [
            self._to_request_model(data) 
            for data in self._requests.values() 
            if data.passenger_id == passenger_id
        ]
    
    async def create(self, request_data: dict) -> TripRequest:
        """Create new request"""
        # Use provided ID if present, otherwise generate new one
        request_id = request_data.get("id") or uuid4()
        data = RequestData(
            id=request_id,
            trip_id=request_data["trip_id"],
            passenger_id=request_data["passenger_id"],
            seats=request_data.get("seats_requested", request_data.get("seats", 1)),
            status=request_data.get("status", "pending"),
            message=request_data.get("message")
        )
        self._requests[request_id] = data
        return self._to_request_model(data)
    
    async def update_status(self, request_id: UUID, new_status: str) -> Optional[TripRequest]:
        """Update request status"""
        data = self._requests.get(request_id)
        if not data:
            return None
        
        data.status = new_status
        data.updated_at = datetime.utcnow()
        return self._to_request_model(data)
    
    async def delete(self, request_id: UUID) -> bool:
        """Delete request"""
        if request_id in self._requests:
            del self._requests[request_id]
            return True
        return False
    
    async def list_all(self) -> List[TripRequest]:
        """List all requests"""
        return [self._to_request_model(data) for data in self._requests.values()]
    
    async def get_pending_by_trip(self, trip_id: UUID) -> List[TripRequest]:
        """Get pending requests for a trip"""
        return [
            self._to_request_model(data)
            for data in self._requests.values()
            if data.trip_id == trip_id and data.status == "pending"
        ]
    
    async def list_by_trip(self, trip_id: UUID) -> List[TripRequest]:
        """List requests by trip (alias for get_by_trip)"""
        return await self.get_by_trip(trip_id)
    
    async def list_by_passenger(self, passenger_id: UUID) -> List[TripRequest]:
        """List requests by passenger (alias for get_by_passenger)"""
        return await self.get_by_passenger(passenger_id)
    
    async def exists(self, trip_id: UUID, passenger_id: UUID) -> bool:
        """Check if request exists for trip and passenger"""
        for data in self._requests.values():
            if data.trip_id == trip_id and data.passenger_id == passenger_id:
                return True
        return False