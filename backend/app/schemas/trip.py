"""Trip Pydantic schemas (DTOs)"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# ================== Enums ==================

class TripStatus(str):
    """Trip status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ================== Response DTOs ==================

class TripResponse(BaseModel):
    """Response DTO for Trip"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    driver_id: UUID
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str
    created_at: datetime


class TripWithDriverResponse(BaseModel):
    """Response DTO for Trip with driver info"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    driver_id: UUID
    driver: Optional[dict] = None  # UserShortResponse serialized
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    status: str


class TripDriverResponse(BaseModel):
    """Response DTO for driver's trip (with passenger count)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    status: str
    passengers_count: int


# ================== Create DTOs ==================

class TripCreate(BaseModel):
    """Create DTO for Trip"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    from_city: str
    to_city: str
    departure_date: str  # YYYY-MM-DD
    departure_time: str   # HH:MM
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None


class TripCreateInternal(BaseModel):
    """Internal Create DTO for Trip (used by services)"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    driver_id: UUID
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str = "active"


# ================== Update DTOs ==================

class TripUpdate(BaseModel):
    """Update DTO for Trip"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    departure_date: Optional[str] = None
    departure_time: Optional[str] = None
    available_seats: Optional[int] = None
    price_per_seat: Optional[int] = None
    description: Optional[str] = None


# ================== Filter DTOs ==================

class TripSearchFilters(BaseModel):
    """Search filters for Trip"""
    from_city: str
    to_city: str
    date: Optional[str] = None


# ================== Pagination DTOs ==================

class PaginatedTripsResponse(BaseModel):
    """Paginated response for trips"""
    items: list
    total: int
    page: int
    page_size: int
    pages: int