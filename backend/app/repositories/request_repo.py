"""In-memory Request Repository"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

from app.models.request import TripRequest
from app.repositories.interfaces import IRequestRepository


class InMemoryRequestRepository(IRequestRepository):
    """In-memory реализация RequestRepository"""
    
    def __init__(self):
        self._requests: dict[UUID, TripRequest] = {}
    
    async def create(self, request_data: dict) -> TripRequest:
        request_id = uuid4()
        request = TripRequest(
            id=request_id,
            trip_id=request_data["trip_id"],
            passenger_id=request_data["passenger_id"],
            seats_requested=request_data["seats_requested"],
            message=request_data.get("message"),
            status=request_data.get("status", "pending"),
            created_at=datetime.utcnow()
        )
        self._requests[request_id] = request
        return request
    
    async def get_by_id(self, request_id: UUID) -> Optional[TripRequest]:
        return self._requests.get(request_id)
    
    async def get_by_trip(self, trip_id: UUID) -> List[TripRequest]:
        return [
            req for req in self._requests.values()
            if req.trip_id == trip_id
        ]
    
    async def get_by_passenger(self, passenger_id: UUID) -> List[TripRequest]:
        return [
            req for req in self._requests.values()
            if req.passenger_id == passenger_id
        ]
    
    async def update_status(self, request_id: UUID, status: str) -> Optional[TripRequest]:
        if request_id not in self._requests:
            return None
        request = self._requests[request_id]
        request.status = status
        request.updated_at = datetime.utcnow()
        return request
    
    async def exists(self, trip_id: UUID, passenger_id: UUID) -> bool:
        for req in self._requests.values():
            if req.trip_id == trip_id and req.passenger_id == passenger_id:
                return True
        return False
