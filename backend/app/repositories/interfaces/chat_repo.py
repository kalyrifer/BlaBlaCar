"""Chat repository interface"""
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.models.chat import Conversation, Message


class ChatRepositoryInterface(ABC):
    """Abstract interface for chat storage"""
    
    @abstractmethod
    async def create_conversation(
        self, 
        trip_id: UUID, 
        driver_id: UUID, 
        passenger_id: UUID
    ) -> Conversation:
        """Create a new conversation"""
        pass
    
    @abstractmethod
    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        """Get conversation by ID"""
        pass
    
    @abstractmethod
    async def get_conversation_by_trip_and_users(
        self, 
        trip_id: UUID, 
        driver_id: UUID, 
        passenger_id: UUID
    ) -> Optional[Conversation]:
        """Get conversation by trip and participants"""
        pass
    
    @abstractmethod
    async def get_user_conversations(self, user_id: UUID) -> List[Conversation]:
        """Get all conversations for a user"""
        pass
    
    @abstractmethod
    async def create_message(
        self, 
        conversation_id: UUID, 
        sender_id: UUID, 
        content: str
    ) -> Message:
        """Create a new message"""
        pass
    
    @abstractmethod
    async def get_messages(
        self, 
        conversation_id: UUID, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Message]:
        """Get messages in a conversation"""
        pass
    
    @abstractmethod
    async def mark_messages_as_read(
        self, 
        conversation_id: UUID, 
        user_id: UUID
    ) -> None:
        """Mark all messages as read for a user"""
        pass
    
    @abstractmethod
    async def get_unread_count(
        self, 
        conversation_id: UUID, 
        user_id: UUID
    ) -> int:
        """Get unread message count for a user"""
        pass
