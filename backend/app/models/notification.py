"""Domain model - Notification"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class Notification(BaseModel):
    """Notification domain model"""
    id: UUID
    user_id: UUID
    type: str  # request_received, request_confirmed, etc.
    title: str
    message: str
    is_read: bool = False
    related_trip_id: Optional[UUID] = None
    related_request_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class NotificationType:
    REQUEST_RECEIVED = "request_received"
    REQUEST_CONFIRMED = "request_confirmed"
    REQUEST_REJECTED = "request_rejected"
    TRIP_CANCELLED = "trip_cancelled"
