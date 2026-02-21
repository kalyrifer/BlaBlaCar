"""Domain model - Trip Request"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class TripRequest(BaseModel):
    """Trip request domain model"""
    id: UUID
    trip_id: UUID
    passenger_id: UUID
    seats_requested: int
    message: Optional[str] = None
    status: str  # pending, confirmed, rejected
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RequestStatus:
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
