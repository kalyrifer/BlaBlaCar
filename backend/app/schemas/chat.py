"""Chat Pydantic schemas (DTOs)"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict


# ================== Response DTOs ==================

class ConversationResponse(BaseModel):
    """Conversation response DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    trip_id: UUID
    driver_id: UUID
    passenger_id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None


class MessageResponse(BaseModel):
    """Message response DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    is_read: bool
    created_at: datetime


class ConversationListItem(BaseModel):
    """Conversation list item for UI"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    trip_id: UUID
    other_user_id: UUID
    other_user_name: str
    trip_from_city: str
    trip_to_city: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0


class MessageListResponse(BaseModel):
    """List response for messages"""
    items: list[MessageResponse]
    total: int


class ConversationListResponse(BaseModel):
    """List response for conversations"""
    items: list[ConversationListItem]
    total: int


# ================== Create DTOs ==================

class MessageCreate(BaseModel):
    """Create DTO for Message"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    conversation_id: UUID
    content: str


class ConversationCreate(BaseModel):
    """Create DTO for Conversation"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    trip_id: UUID
    passenger_id: UUID


# ================== Update DTOs ==================

class MessageMarkRead(BaseModel):
    """Update DTO for marking message as read"""
    is_read: bool = True