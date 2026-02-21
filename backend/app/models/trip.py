"""Domain model - Trip"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class Trip(BaseModel):
    """Trip domain model"""
    id: UUID
    driver_id: UUID
    from_city: str
    to_city: str
    departure_date: str  # YYYY-MM-DD
    departure_time: str  # HH:MM
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str  # active, completed, cancelled
    created_at: datetime
    
    class Config:
        from_attributes = True


class TripStatus:
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
