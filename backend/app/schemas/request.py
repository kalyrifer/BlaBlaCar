"""Request Pydantic schemas (DTOs)"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# ================== Enums ==================

class RequestStatus(str):
    """Request status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"


# ================== Response DTOs ==================

class TripRequestResponse(BaseModel):
    """Response DTO for Trip Request"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    trip_id: UUID
    passenger_id: UUID
    passenger: Optional[dict] = None  # UserShortResponse serialized
    seats_requested: int
    message: Optional[str] = None
    status: str
    created_at: datetime
    updated_at: Optional[datetime] = None


class TripRequestPassengerResponse(BaseModel):
    """Response DTO for passenger's request view"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    trip_id: UUID
    trip: Optional[dict] = None  # Trip info for passenger
    seats_requested: int
    status: str
    created_at: datetime


class TripRequestDriverResponse(BaseModel):
    """Response DTO for driver's request view"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    passenger_id: UUID
    passenger: Optional[dict] = None  # UserShortResponse serialized
    seats_requested: int
    message: Optional[str] = None
    status: str
    created_at: datetime


# ================== Create DTOs ==================

class RequestCreate(BaseModel):
    """Create DTO for Trip Request"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    trip_id: UUID
    seats_requested: int = 1
    message: Optional[str] = None


class RequestCreateInternal(BaseModel):
    """Internal Create DTO for Trip Request (used by services)"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    trip_id: UUID
    passenger_id: UUID
    seats_requested: int
    message: Optional[str] = None
    status: str = "pending"


# ================== Update DTOs ==================

class RequestStatusUpdate(BaseModel):
    """Update DTO for Request status"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    status: str


# ================== Pagination DTOs ==================

class PaginatedRequestsResponse(BaseModel):
    """Paginated response for requests"""
    items: list
    total: int
    page: int
    page_size: int
    pages: int