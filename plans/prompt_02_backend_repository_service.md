# Промпт 2: Backend — Репозиторий и сервис чата

## Задача

Создать слой репозитория и сервис для системы чата в проекте RoadMate.

## Требования к проекту

- Проект: RoadMate — веб-приложение для карпулинга на FastAPI
- Backend использует: async/await, паттерн репозитория
- Уже созданы модели из промпта 1: `backend/app/models/chat.py`, `backend/app/db/models/chat.py`, `backend/app/schemas/chat.py`

## Справочная информация

В проекте используется паттерн репозитория с интерфейсами. Пример интерфейса:

```python
# backend/app/repositories/interfaces/user_repo.py
from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional, List
from app.models.user import User

class UserRepositoryInterface(ABC):
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        pass
```

## Задание

### 1. Создать интерфейс репозитория

Создать файл `backend/app/repositories/interfaces/chat_repo.py`:

```python
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
```

### 2. Создать in-memory реализацию репозитория

Создать файл `backend/app/repositories/inmemory/chat_repo.py`:

```python
"""In-memory chat repository implementation"""
from uuid import UUID
from typing import Optional, List, Dict
from datetime import datetime
import uuid

from app.models.chat import Conversation, Message
from app.repositories.interfaces.chat_repo import ChatRepositoryInterface


class InMemoryChatRepository(ChatRepositoryInterface):
    """In-memory implementation of chat repository"""
    
    def __init__(self):
        self._conversations: Dict[UUID, Conversation] = {}
        self._messages: Dict[UUID, List[Message]] = {}
    
    async def create_conversation(
        self, 
        trip_id: UUID, 
        driver_id: UUID, 
        passenger_id: UUID
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
    
    async def get_conversation(self, conversation_id: UUID) -> Optional[Conversation]:
        return self._conversations.get(conversation_id)
    
    async def get_conversation_by_trip_and_users(
        self, 
        trip_id: UUID, 
        driver_id: UUID, 
        passenger_id: UUID
    ) -> Optional[Conversation]:
        for conv in self._conversations.values():
            if (conv.trip_id == trip_id and 
                conv.driver_id == driver_id and 
                conv.passenger_id == passenger_id):
                return conv
        return None
    
    async def get_user_conversations(self, user_id: UUID) -> List[Conversation]:
        return [
            conv for conv in self._conversations.values()
            if conv.driver_id == user_id or conv.passenger_id == user_id
        ]
    
    async def create_message(
        self, 
        conversation_id: UUID, 
        sender_id: UUID, 
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
        conversation_id: UUID, 
        skip: int = 0, 
        limit: int = 50
    ) -> List[Message]:
        messages = self._messages.get(conversation_id, [])
        return messages[skip:skip + limit]
    
    async def mark_messages_as_read(
        self, 
        conversation_id: UUID, 
        user_id: UUID
    ) -> None:
        if conversation_id in self._messages:
            for msg in self._messages[conversation_id]:
                if msg.sender_id != user_id:
                    msg.is_read = True
    
    async def get_unread_count(
        self, 
        conversation_id: UUID, 
        user_id: UUID
    ) -> int:
        messages = self._messages.get(conversation_id, [])
        return sum(
            1 for msg in messages 
            if msg.sender_id != user_id and not msg.is_read
        )
```

### 3. Создать сервис чата

Создать файл `backend/app/services/chat_service.py`:

```python
"""Chat service - business logic for chat"""
from uuid import UUID
from typing import List
from app.repositories.interfaces.chat_repo import ChatRepositoryInterface
from app.models.chat import Conversation, Message
from app.schemas.chat import ConversationListItem, MessageResponse


class ChatService:
    """Service for managing conversations and messages"""
    
    def __init__(self, chat_repo: ChatRepositoryInterface):
        self.chat_repo = chat_repo
    
    async def get_or_create_conversation(
        self,
        trip_id: UUID,
        driver_id: UUID,
        passenger_id: UUID
    ) -> Conversation:
        """Get existing conversation or create new one"""
        existing = await self.chat_repo.get_conversation_by_trip_and_users(
            trip_id, driver_id, passenger_id
        )
        if existing:
            return existing
        
        return await self.chat_repo.create_conversation(
            trip_id, driver_id, passenger_id
        )
    
    async def get_user_conversations(
        self,
        user_id: UUID,
        trip_repo,  # TripRepositoryInterface - нужно передать при вызове
        user_repo   # UserRepositoryInterface - нужно передать при вызове
    ) -> List[ConversationListItem]:
        """Get all conversations for a user with metadata"""
        conversations = await self.chat_repo.get_user_conversations(user_id)
        
        result = []
        for conv in conversations:
            # Determine the other user
            other_user_id = conv.passenger_id if conv.driver_id == user_id else conv.driver_id
            other_user = await user_repo.get_by_id(other_user_id)
            
            # Get trip info
            trip = await trip_repo.get_by_id(conv.trip_id)
            
            # Get last message and unread count
            messages = await self.chat_repo.get_messages(conv.id, skip=0, limit=1)
            last_message = messages[0] if messages else None
            unread_count = await self.chat_repo.get_unread_count(conv.id, user_id)
            
            result.append(ConversationListItem(
                id=conv.id,
                trip_id=conv.trip_id,
                other_user_id=other_user_id,
                other_user_name=other_user.name if other_user else "Unknown",
                trip_from_city=trip.from_city if trip else "",
                trip_to_city=trip.to_city if trip else "",
                last_message=last_message.content if last_message else None,
                last_message_time=last_message.created_at if last_message else None,
                unread_count=unread_count
            ))
        
        # Sort by last message time
        result.sort(key=lambda x: x.last_message_time or x.created_at, reverse=True)
        return result
    
    async def get_conversation_messages(
        self,
        conversation_id: UUID,
        user_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[MessageResponse]:
        """Get messages in a conversation"""
        messages = await self.chat_repo.get_messages(conversation_id, skip, limit)
        
        # Mark messages as read
        await self.chat_repo.mark_messages_as_read(conversation_id, user_id)
        
        return [
            MessageResponse(
                id=m.id,
                conversation_id=m.conversation_id,
                sender_id=m.sender_id,
                content=m.content,
                is_read=m.is_read,
                created_at=m.created_at
            )
            for m in messages
        ]
    
    async def send_message(
        self,
        conversation_id: UUID,
        sender_id: UUID,
        content: str
    ) -> MessageResponse:
        """Send a message in a conversation"""
        message = await self.chat_repo.create_message(
            conversation_id, sender_id, content
        )
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            sender_id=message.sender_id,
            content=message.content,
            is_read=message.is_read,
            created_at=message.created_at
        )
```

## Критерии приёмки

- [ ] Файл `backend/app/repositories/interfaces/chat_repo.py` создан с полным интерфейсом
- [ ] Файл `backend/app/repositories/inmemory/chat_repo.py` создан с рабочей in-memory реализацией
- [ ] Файл `backend/app/services/chat_service.py` создан с бизнес-логикой
- [ ] Метод `get_or_create_conversation` не создаёт дубликаты
- [ ] Метод `mark_messages_as_read` не помечает свои собственные сообщения
- [ ] Сервис использует передаваемые trip_repo и user_repo для получения мета-данных