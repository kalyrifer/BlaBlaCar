# Подробная инструкция по созданию чата между пользователями

## Оглавление

1. [Обзор требований](#1-обзор-требований)
2. [Архитектура системы](#2-архитектура-системы)
3. [Backend - Слой данных](#3-backend---слой-данных)
4. [Backend - API эндпоинты](#4-backend---api-эндпоинты)
5. [Frontend - Типы и сервисы](#5-frontend---типы-и-сервисы)
6. [Frontend - Компоненты UI](#6-frontend---компоненты-ui)
7. [Frontend - Страницы и маршрутизация](#7-frontend---страницы-и-маршрутизация)
8. [Интеграция с существующими функциями](#8-интеграция-с-существующими-функциями)

---

## 1. Обзор требований

### Описание функциональности

Чат между водителем и пассажиром после подтверждения заявки на поездку.

### Сценарий использования

1. Пассажир отправляет заявку на поездку
2. Водитель подтверждает заявку (статус `confirmed`)
3. После подтверждения автоматически создаётся чат между водителем и пассажиром
4. Оба пользователя могут обмениваться сообщениями в чате
5. Чат связан с конкретной поездкой

### Основные сущности

- **Conversation (Беседа)** — содержит информацию об участниках и поездке
- **Message (Сообщение)** — текстовое сообщение от пользователя

---

## 2. Архитектура системы

### Структура проекта

```
backend/app/
├── api/
│   ├── chat.py              # API эндпоинты чата (НОВЫЙ)
├── db/models/
│   ├── chat.py              # SQLAlchemy модели (НОВЫЙ)
├── schemas/
│   ├── chat.py              # Pydantic схемы (НОВЫЙ)
├── services/
│   ├── chat_service.py      # Бизнес-логика чата (НОВЫЙ)
├── repositories/interfaces/
│   ├── chat_repo.py         # Интерфейс репозитория (НОВЫЙ)
├── repositories/inmemory/
│   ├── chat_repo.py         # In-memory реализация (НОВЫЙ)
├── repositories/db/
│   ├── pg_chat_repo.py     # PostgreSQL реализация (НОВЫЙ)

frontend/src/
├── types/
│   └── index.ts             # Добавить типы чата
├── services/
│   └── api.ts              # Добавить API методы
├── components/chat/
│   ├── ChatList.tsx        # Список чатов (НОВЫЙ)
│   ├── ChatWindow.tsx      # Окно чата (НОВЫЙ)
│   ├── MessageBubble.tsx   # Пузырь сообщения (НОВЫЙ)
│   └── ChatPage.tsx        # Страница чата (НОВЫЙ)
├── pages/
│   └── MessagesPage.tsx    # Страница сообщений (НОВЫЙ)
└── App.tsx                 # Добавить маршрут
```

---

## 3. Backend - Слой данных

### 3.1 Доменные модели (Pydantic)

Создать файл `backend/app/models/chat.py`:

```python
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
```

### 3.2 SQLAlchemy модели

Создать файл `backend/app/db/models/chat.py`:

```python
"""SQLAlchemy chat models"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.db.models.base import Base
import uuid


class ConversationModel(Base):
    """Conversation database model"""
    __tablename__ = "conversations"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(PGUUID(as_uuid=True), ForeignKey("trips.id"), nullable=False)
    driver_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    passenger_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")


class MessageModel(Base):
    """Message database model"""
    __tablename__ = "messages"
    
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(PGUUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    conversation = relationship("ConversationModel", back_populates="messages")
```

### 3.3 Интерфейс репозитория

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

### 3.4 Pydantic схемы

Создать файл `backend/app/schemas/chat.py`:

```python
"""Chat Pydantic schemas (DTOs)"""
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    """Create conversation DTO"""
    trip_id: UUID
    driver_id: UUID
    passenger_id: UUID


class ConversationResponse(BaseModel):
    """Conversation response DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    trip_id: UUID
    driver_id: UUID
    passenger_id: UUID
    created_at: datetime
    updated_at: datetime


class MessageCreate(BaseModel):
    """Create message DTO"""
    content: str


class MessageResponse(BaseModel):
    """Message response DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    conversation_id: UUID
    sender_id: UUID
    content: str
    is_read: bool
    created_at: datetime


class ConversationWithMessages(BaseModel):
    """Conversation with last message"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    trip_id: UUID
    driver_id: UUID
    passenger_id: UUID
    created_at: datetime
    updated_at: datetime
    last_message: Optional[MessageResponse] = None
    unread_count: int = 0


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
```

### 3.5 Сервис чата

Создать файл `backend/app/services/chat_service.py`:

```python
"""Chat service - business logic for chat"""
from uuid import UUID
from typing import List, Optional
from app.repositories.interfaces.chat_repo import ChatRepositoryInterface
from app.models.chat import Conversation, Message
from app.schemas.chat import (
    ConversationCreate,
    ConversationListItem,
    MessageResponse,
)


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
        trip_repo,  # TripRepositoryInterface
        user_repo   # UserRepositoryInterface
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

---

## 4. Backend - API эндпоинты

### 4.1 Создание API роутера

Создать файл `backend/app/api/chat.py`:

```python
"""Chat API endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    ConversationListItem,
)
from app.services.chat_service import ChatService
from app.core.database import get_db


router = APIRouter()


class SendMessageRequest(BaseModel):
    """Request to send a message"""
    content: str


@router.get("/conversations", response_model=list[ConversationListItem])
async def get_my_conversations(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(lambda: get_db().chat)
):
    """Get all conversations for current user"""
    from app.services.trip_service import TripService
    from app.repositories.interfaces.trip_repo import TripRepositoryInterface
    from app.repositories.interfaces.user_repo import UserRepositoryInterface
    
    trip_service: TripService = None  # Get from deps
    user_repo: UserRepositoryInterface = None  # Get from deps
    
    return await chat_service.get_user_conversations(
        current_user.id,
        trip_service,  # Pass trip repo
        user_repo      # Pass user repo
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(lambda: get_db().chat)
):
    """Get messages in a conversation"""
    try:
        conv_id = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    messages = await chat_service.get_conversation_messages(
        conv_id, current_user.id, skip, limit
    )
    return messages


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse)
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(lambda: get_db().chat)
):
    """Send a message in a conversation"""
    try:
        conv_id = UUID(conversation_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid conversation ID")
    
    message = await chat_service.send_message(
        conv_id, current_user.id, request.content
    )
    return message


@router.post("/trips/{trip_id}/conversation")
async def get_or_create_conversation(
    trip_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get or create conversation for a trip (after request is confirmed)"""
    from app.core.database import get_db
    from app.services.request_service import RequestService
    
    try:
        trip_uuid = UUID(trip_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid trip ID")
    
    db = get_db()
    
    # Get trip info
    trip = await db.trips.get_by_id(trip_uuid)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Check if user is either driver or passenger
    is_driver = trip.driver_id == current_user.id
    
    # Get passenger (the other user)
    if is_driver:
        # Driver looking for passenger - need to find confirmed requests
        requests = await db.requests.get_by_trip(trip_uuid)
        confirmed_requests = [r for r in requests if r.status.value == "confirmed"]
        
        if not confirmed_requests:
            raise HTTPException(
                status_code=400, 
                detail="No confirmed passengers for this trip"
            )
        
        # Create conversation with first confirmed passenger
        passenger_id = confirmed_requests[0].passenger_id
    else:
        # Passenger looking for driver
        # Check if user has confirmed request for this trip
        requests = await db.requests.get_by_passenger(current_user.id)
        trip_request = next(
            (r for r in requests if r.trip_id == trip_uuid and r.status.value == "confirmed"),
            None
        )
        
        if not trip_request:
            raise HTTPException(
                status_code=403,
                detail="You don't have a confirmed request for this trip"
            )
        
        passenger_id = current_user.id
    
    # Get or create conversation
    chat_service = db.chat
    conversation = await chat_service.get_or_create_conversation(
        trip_uuid,
        trip.driver_id,
        passenger_id
    )
    
    return {
        "id": str(conversation.id),
        "trip_id": str(conversation.trip_id),
        "driver_id": str(conversation.driver_id),
        "passenger_id": str(conversation.passenger_id)
    }
```

### 4.2 Подключение роутера в main.py

Добавить в `backend/app/main.py`:

```python
from app.api.chat import router as chat_router

# Добавить в функцию create_application() или аналогичную
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
```

---

## 5. Frontend - Типы и сервисы

### 5.1 Добавление типов чата

Добавить в `frontend/src/types/index.ts`:

```typescript
// Chat types
export interface Conversation {
  id: string;
  trip_id: string;
  other_user_id: string;
  other_user_name: string;
  trip_from_city: string;
  trip_to_city: string;
  last_message?: string;
  last_message_time?: string;
  unread_count: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  trip_id: string;
  driver_id: string;
  passenger_id: string;
}
```

### 5.2 Добавление API методов

Добавить в `frontend/src/services/api.ts`:

```typescript
// Chat API
export const chatApi = {
  // Get all conversations for current user
  getConversations: () => 
    axiosInstance.get<Conversation[]>('/chat/conversations'),
  
  // Get or create conversation for a trip
  getOrCreateConversation: (tripId: string) =>
    axiosInstance.post<ConversationDetail>(`/chat/trips/${tripId}/conversation`),
  
  // Get messages in a conversation
  getMessages: (conversationId: string, skip = 0, limit = 50) =>
    axiosInstance.get<Message[]>(
      `/chat/conversations/${conversationId}/messages`,
      { params: { skip, limit } }
    ),
  
  // Send a message
  sendMessage: (conversationId: string, content: string) =>
    axiosInstance.post<Message>(
      `/chat/conversations/${conversationId}/messages`,
      { content }
    ),
};

// Update api export
export const api = {
  // ... existing exports
  // Chat
  getConversations: chatApi.getConversations,
  getOrCreateConversation: chatApi.getOrCreateConversation,
  getMessages: chatApi.getMessages,
  sendMessage: chatApi.sendMessage,
};
```

---

## 6. Frontend - Компоненты UI

### 6.1 Компонент списка чатов

Создать `frontend/src/components/chat/ChatList.tsx`:

```tsx
import { Link } from 'react-router-dom';
import type { Conversation } from '../../types';

interface ChatListProps {
  conversations: Conversation[];
}

export function ChatList({ conversations }: ChatListProps) {
  if (conversations.length === 0) {
    return (
      <div className="empty-state">
        <p>У вас пока нет чатов</p>
        <p>Чаты появятся после подтверждения заявки на поездку</p>
      </div>
    );
  }

  return (
    <div className="chat-list">
      {conversations.map((conv) => (
        <Link
          key={conv.id}
          to={`/messages/${conv.id}`}
          className="chat-list-item"
        >
          <div className="chat-list-avatar">
            {conv.other_user_name.charAt(0).toUpperCase()}
          </div>
          <div className="chat-list-content">
            <div className="chat-list-header">
              <span className="chat-list-name">{conv.other_user_name}</span>
              {conv.last_message_time && (
                <span className="chat-list-time">
                  {new Date(conv.last_message_time).toLocaleDateString('ru-RU')}
                </span>
              )}
            </div>
            <div className="chat-list-route">
              {conv.trip_from_city} → {conv.trip_to_city}
            </div>
            {conv.last_message && (
              <div className="chat-list-preview">{conv.last_message}</div>
            )}
          </div>
          {conv.unread_count > 0 && (
            <div className="chat-list-badge">{conv.unread_count}</div>
          )}
        </Link>
      ))}
    </div>
  );
}
```

### 6.2 Компонент пузыря сообщения

Создать `frontend/src/components/chat/MessageBubble.tsx`:

```tsx
import type { Message } from '../../types';
import { useAuthStore } from '../../stores/auth';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const user = useAuthStore((state) => state.user);
  const isOwn = message.sender_id === user?.id;

  return (
    <div className={`message-bubble ${isOwn ? 'message-own' : 'message-other'}`}>
      <div className="message-content">{message.content}</div>
      <div className="message-time">
        {new Date(message.created_at).toLocaleTimeString('ru-RU', {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </div>
  );
}
```

### 6.3 Компонент окна чата

Создать `frontend/src/components/chat/ChatWindow.tsx`:

```tsx
import { useState, useRef, useEffect } from 'react';
import { chatApi } from '../../services/api';
import { MessageBubble } from './MessageBubble';
import type { Message } from '../../types';

interface ChatWindowProps {
  conversationId: string;
  messages: Message[];
  onNewMessage: (message: Message) => void;
}

export function ChatWindow({ conversationId, messages, onNewMessage }: ChatWindowProps) {
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!newMessage.trim() || sending) return;
    
    setSending(true);
    try {
      const response = await chatApi.sendMessage(conversationId, newMessage.trim());
      onNewMessage(response.data);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="chat-input-container">
        <textarea
          className="chat-input"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Введите сообщение..."
          rows={2}
        />
        <button
          className="btn btn-primary chat-send-btn"
          onClick={handleSend}
          disabled={sending || !newMessage.trim()}
        >
          {sending ? '...' : 'Отправить'}
        </button>
      </div>
    </div>
  );
}
```

---

## 7. Frontend - Страницы и маршрутизация

### 7.1 Страница списка сообщений

Создать `frontend/src/pages/MessagesPage.tsx`:

```tsx
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import { ChatList } from '../components/chat/ChatList';
import type { Conversation } from '../types';

export default function MessagesPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await api.getConversations();
        setConversations(response.data);
      } catch (error) {
        console.error('Error fetching conversations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
  }, []);

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  return (
    <div className="messages-page">
      <div className="page-header">
        <h1>Сообщения</h1>
      </div>
      
      <ChatList conversations={conversations} />
    </div>
  );
}
```

### 7.2 Страница конкретного чата

Создать `frontend/src/pages/ChatPage.tsx`:

```tsx
import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { ChatWindow } from '../components/chat/ChatWindow';
import type { Message } from '../types';

export default function ChatPage() {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchMessages = useCallback(async () => {
    if (!id) return;
    try {
      const response = await api.getMessages(id);
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchMessages();
    
    // Poll for new messages every 5 seconds
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, [fetchMessages]);

  const handleNewMessage = (message: Message) => {
    setMessages((prev) => [...prev, message]);
  };

  if (loading) {
    return <div className="loading">Загрузка...</div>;
  }

  if (!id) {
    return <div>Чат не найден</div>;
  }

  return (
    <div className="chat-page">
      <div className="chat-page-header">
        <Link to="/messages" className="back-link">
          ← Назад к сообщениям
        </Link>
      </div>
      
      <ChatWindow
        conversationId={id}
        messages={messages}
        onNewMessage={handleNewMessage}
      />
    </div>
  );
}
```

### 7.3 Добавление маршрутов

Обновить `frontend/src/App.tsx`:

```tsx
import { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';

// Add these lazy imports
const MessagesPage = lazy(() => import('./pages/MessagesPage'));
const ChatPage = lazy(() => import('./pages/ChatPage'));

// Add these routes in the Routes component
<Route path="messages" element={
  <ProtectedRoute>
    <MessagesPage />
  </ProtectedRoute>
} />
<Route path="messages/:id" element={
  <ProtectedRoute>
    <ChatPage />
  </ProtectedRoute>
} />
```

---

## 8. Интеграция с существующими функциями

### 8.1 Добавление кнопки "Написать" на странице поездки

Обновить `frontend/src/pages/TripPage.tsx`, добавив кнопку для перехода в чат:

```tsx
import { Link } from 'react-router-dom';

// В компоненте TripPage, после информации о водителе:
// Добавить кнопку для открытия чата (если пользователь - пассажир с подтверждённой заявкой)

{!isOwner && isAuthenticated && trip.status === 'active' && (
  <Link 
    to={`/messages/${trip.id}`} 
    className="btn btn-secondary"
    style={{ width: '100%', marginTop: '12px' }}
  >
    Написать водителю
  </Link>
)}
```

### 8.2 Создание чата при подтверждении заявки

Модифицировать `backend/app/services/request_service.py` для автоматического создания чата:

```python
async def confirm_request(self, request_id: UUID, driver_id: UUID):
    """Confirm a trip request - creates conversation for chat"""
    # ... existing logic ...
    
    # After confirming, create conversation
    from app.core.database import get_db
    db = get_db()
    
    chat_service = db.chat
    await chat_service.get_or_create_conversation(
        trip_id= trip_id,
        driver_id=driver_id,
        passenger_id=passenger_id
    )
```

### 8.3 Добавление в навигацию

Обновить `frontend/src/components/Layout.tsx` для добавления ссылки на сообщения:

```tsx
// В меню навигации добавить:
<Link to="/messages" className="nav-link">
  <span>💬</span>
  <span>Сообщения</span>
</Link>
```

---

## 9. Стили CSS

Добавить стили в `frontend/src/index.css`:

```css
/* Chat List */
.chat-list {
  display: flex;
  flex-direction: column;
}

.chat-list-item {
  display: flex;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
  text-decoration: none;
  color: inherit;
  transition: background 0.2s;
}

.chat-list-item:hover {
  background: #f9fafb;
}

.chat-list-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: #00a8e8;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  margin-right: 12px;
}

.chat-list-content {
  flex: 1;
  min-width: 0;
}

.chat-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.chat-list-name {
  font-weight: 600;
  color: #1a1a2e;
}

.chat-list-time {
  font-size: 12px;
  color: #9ca3af;
}

.chat-list-route {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.chat-list-preview {
  font-size: 14px;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.chat-list-badge {
  background: #00a8e8;
  color: white;
  border-radius: 12px;
  padding: 2px 8px;
  font-size: 12px;
  font-weight: 600;
}

/* Chat Window */
.chat-window {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 200px);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.message-bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 16px;
  word-wrap: break-word;
}

.message-own {
  align-self: flex-end;
  background: #00a8e8;
  color: white;
  border-bottom-right-radius: 4px;
}

.message-other {
  align-self: flex-start;
  background: #f3f4f6;
  color: #1a1a2e;
  border-bottom-left-radius: 4px;
}

.message-content {
  margin-bottom: 4px;
}

.message-time {
  font-size: 11px;
  opacity: 0.7;
  text-align: right;
}

.chat-input-container {
  display: flex;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid #e5e7eb;
  background: white;
}

.chat-input {
  flex: 1;
  padding: 12px;
  border: 2px solid #e5e7eb;
  border-radius: 12px;
  resize: none;
  font-family: inherit;
}

.chat-input:focus {
  outline: none;
  border-color: #00a8e8;
}

.chat-send-btn {
  align-self: flex-end;
}
```

---

## 10. Тестирование

### Backend тесты

Создать `backend/tests/test_chat_service.py`:

```python
"""Tests for chat service"""
import pytest
from uuid import uuid4
from app.services.chat_service import ChatService
from app.repositories.inmemory.chat_repo import InMemoryChatRepository


@pytest.fixture
def chat_repo():
    return InMemoryChatRepository()


@pytest.fixture
def chat_service(chat_repo):
    return ChatService(chat_repo)


@pytest.mark.asyncio
async def test_create_conversation(chat_service):
    trip_id = uuid4()
    driver_id = uuid4()
    passenger_id = uuid4()
    
    conv = await chat_service.get_or_create_conversation(
        trip_id, driver_id, passenger_id
    )
    
    assert conv.trip_id == trip_id
    assert conv.driver_id == driver_id
    assert conv.passenger_id == passenger_id


@pytest.mark.asyncio
async def test_get_existing_conversation(chat_service):
    trip_id = uuid4()
    driver_id = uuid4()
    passenger_id = uuid4()
    
    conv1 = await chat_service.get_or_create_conversation(
        trip_id, driver_id, passenger_id
    )
    
    conv2 = await chat_service.get_or_create_conversation(
        trip_id, driver_id, passenger_id
    )
    
    assert conv1.id == conv2.id


@pytest.mark.asyncio
async def test_send_message(chat_service):
    trip_id = uuid4()
    driver_id = uuid4()
    passenger_id = uuid4()
    
    conv = await chat_service.get_or_create_conversation(
        trip_id, driver_id, passenger_id
    )
    
    message = await chat_service.send_message(
        conv.id, driver_id, "Hello!"
    )
    
    assert message.content == "Hello!"
    assert message.sender_id == driver_id
```

---

## Резюме

Данная инструкция описывает полную реализацию системы чата между водителем и пассажиром:

### Основные компоненты:

1. **Backend:**
   - SQLAlchemy модели (`Conversation`, `Message`)
   - Репозиторий с интерфейсом
   - Pydantic схемы для валидации
   - Сервис с бизнес-логикой
   - API эндпоинты

2. **Frontend:**
   - TypeScript типы
   - API методы
   - React компоненты (ChatList, MessageBubble, ChatWindow)
   - Страницы (MessagesPage, ChatPage)
   - Маршрутизация
   - CSS стили

### Ключевые сценарии:
- Чат создаётся автоматически после подтверждения заявки
- Пользователи видят список своих чатов
- Пользователи могут отправлять и получать сообщения
- Реализовано автоматическое обновление сообщений
