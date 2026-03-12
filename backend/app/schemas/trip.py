"""Trip Pydantic schemas (DTOs)"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Union


# ================== Enums ==================

class TripStatus(str):
    """Trip status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# ================== Helper functions ==================

def parse_datetime(value: Union[str, datetime]) -> datetime:
    """Parse datetime from string or return as-is, convert to UTC."""
    if isinstance(value, datetime):
        # If datetime has no timezone, assume local and convert to UTC
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        # Convert to UTC
        return value.astimezone(timezone.utc)
    
    # Try parsing ISO format
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
            if dt.tzinfo is None:
                return dt.replace(tzinfo=timezone.utc)
            return dt.astimezone(timezone.utc)
        except ValueError:
            pass
        
        # Try common formats
        formats = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M",
        ]
        for fmt in formats:
            try:
                dt = datetime.strptime(value, fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    
    raise ValueError(f"Cannot parse datetime: {value}")


# ================== Response DTOs ==================

class TripResponse(BaseModel):
    """Response DTO for Trip"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    driver_id: UUID
    from_city: str
    to_city: str
    departure_at: datetime
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
    departure_at: datetime
    available_seats: int
    price_per_seat: int
    status: str


class TripDriverResponse(BaseModel):
    """Response DTO for driver's trip (with passenger count)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    from_city: str
    to_city: str
    departure_at: datetime
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
    departure_at: Union[str, datetime]  # ISO datetime or string
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    
    @field_validator('departure_at', mode='before')
    @classmethod
    def convert_departure_at_to_utc(cls, v: Union[str, datetime]) -> datetime:
        """Convert departure_at to UTC datetime."""
        return parse_datetime(v)


class TripCreateInternal(BaseModel):
    """Internal Create DTO for Trip (used by services)"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    driver_id: UUID
    from_city: str
    to_city: str
    departure_at: datetime
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
    departure_at: Optional[Union[str, datetime]] = None
    available_seats: Optional[int] = None
    price_per_seat: Optional[int] = None
    description: Optional[str] = None
    
    @field_validator('departure_at', mode='before')
    @classmethod
    def convert_departure_at_to_utc(cls, v: Optional[Union[str, datetime]]) -> Optional[datetime]:
        """Convert departure_at to UTC datetime if provided."""
        if v is None:
            return None
        return parse_datetime(v)


# ================== Filter DTOs ==================

class TripSearchFilters(BaseModel):
    """Search filters for Trip"""
    from_city: str
    to_city: str
    date_from: Optional[Union[str, datetime]] = None  # Filter trips >= this datetime
    date_to: Optional[Union[str, datetime]] = None    # Filter trips <= this datetime
    
    @field_validator('date_from', mode='before')
    @classmethod
    def convert_date_from_to_utc(cls, v: Optional[Union[str, datetime]]) -> Optional[datetime]:
        if v is None:
            return None
        return parse_datetime(v)
    
    @field_validator('date_to', mode='before')
    @classmethod
    def convert_date_to_to_utc(cls, v: Optional[Union[str, datetime]]) -> Optional[datetime]:
        if v is None:
            return None
        return parse_datetime(v)


# ================== Pagination DTOs ==================

class PaginatedTripsResponse(BaseModel):
    """Paginated response for trips"""
    items: list
    total: int
    page: int
    page_size: int
    pages: int
