"""Notification Pydantic schemas (DTOs)"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# ================== Response DTOs ==================

class NotificationResponse(BaseModel):
    """Response DTO for Notification"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    type: str
    title: str
    message: str
    related_trip_id: Optional[UUID] = None
    related_request_id: Optional[UUID] = None
    is_read: bool
    created_at: datetime


class NotificationListResponse(BaseModel):
    """List response for notifications"""
    items: list
    total: int
    unread_count: int


# ================== Create DTOs ==================

class NotificationCreate(BaseModel):
    """Create DTO for Notification"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    user_id: UUID
    type: str
    title: str
    message: str
    related_trip_id: Optional[UUID] = None
    related_request_id: Optional[UUID] = None


# ================== Update DTOs ==================

class NotificationMarkRead(BaseModel):
    """Update DTO for marking notification as read"""
    is_read: bool = True