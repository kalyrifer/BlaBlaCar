"""In-memory chat repository implementation"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from app.models.chat import Conversation, Message
from app.repositories.interfaces.chat_repo import ChatRepositoryInterface


class InMemoryChatRepository(ChatRepositoryInterface):
    """In-memory implementation of chat repository"""
    
    def __init__(self):
        self._conversations: Dict[uuid.UUID, Conversation] = {}
        self._messages: Dict[uuid.UUID, List[Message]] = {}
    
    async def create_conversation(
        self, 
        trip_id: uuid.UUID, 
        driver_id: uuid.UUID, 
        passenger_id: uuid.UUID
    ) -> Conversation:
        now = datetime.utcnow()
        conversation = Conversation(
            id=uuid.uuid4(),
            trip_id=trip_id,
            driver_id=driver_id,
            passenger_id=passenger_id,
            created_at=now,
            updated_at=now
        )
        self._conversations[conversation.id] = conversation
        self._messages[conversation.id] = []
        return conversation
    
    async def get_conversation(self, conversation_id: uuid.UUID) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)
    
    async def get_conversation_by_trip_and_users(
        self, 
        trip_id: uuid.UUID, 
        driver_id: uuid.UUID, 
        passenger_id: uuid.UUID
    ) -> Optional[Conversation]:
        for conv in self._conversations.values():
            if (conv.trip_id == trip_id and 
                conv.driver_id == driver_id and 
                conv.passenger_id == passenger_id):
                return conv
        return None
    
    async def get_user_conversations(self, user_id: uuid.UUID) -> List[Conversation]:
        return [
            conv for conv in self._conversations.values()
            if conv.driver_id == user_id or conv.passenger_id == user_id
        ]
    
    async def create_message(
        self, 
        conversation_id: uuid.UUID, 
        sender_id: uuid.UUID, 
        content: str
    ) -> Message:
        message = Message(
            id=uuid.uuid4(),
            conversation_id=conversation_id,
            sender_id=sender_id,
            content=content,
            is_read=False,
            created_at=datetime.utcnow()
        )
        
        if conversation_id not in self._messages:
            self._messages[conversation_id] = []
        self._messages[conversation_id].append(message)
        
        # Update conversation updated_at
        if conversation_id in self._conversations:
            self._conversations[conversation_id].updated_at = datetime.utcnow()
        
        return message
    
    async def get_messages(
        self, 
        conversation_id: uuid.UUID, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Message]:
        messages = self._messages.get(conversation_id, [])
        return messages[skip:skip + limit]
    
    async def mark_messages_as_read(
        self, 
        conversation_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> None:
        if conversation_id in self._messages:
            for msg in self._messages[conversation_id]:
                if msg.sender_id != user_id:
                    msg.is_read = True
    
    async def get_unread_count(
        self, 
        conversation_id: uuid.UUID, 
        user_id: uuid.UUID
    ) -> int:
        messages = self._messages.get(conversation_id, [])
        return sum(
            1 for msg in messages 
            if msg.sender_id != user_id and not msg.is_read
        )
