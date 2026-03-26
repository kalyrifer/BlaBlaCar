"""Chat domain models"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional


class Conversation(BaseModel):
    """Conversation between driver and passenger"""
    id: UUID
    trip_id: UUID
    driver_id: UUID
    passenger_id: UUID
    created_at: datetime
    updated_at: datetime


class Message(BaseModel):
    """Message in a conversation"""
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    is_read: bool
    created_at: datetime