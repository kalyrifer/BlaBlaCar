# Промпт 1: Backend — Доменные модели и SQLAlchemy

## Задача

Создать слой данных для системы чата в проекте RoadMate (BlaBlaCar).

## Требования к проекту

- Проект: RoadMate — веб-приложение для карпулинга на FastAPI (бэкенд) + React (фронтенд)
- Backend использует: FastAPI, SQLAlchemy 2.0, Pydantic v2, async/await
- Структура проекта: чистая архитектура с разделением на слои (api → services → repositories → models)

## Задание

### 1. Создать доменные модели (Pydantic)

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

### 2. Создать SQLAlchemy модели

Создать файл `backend/app/db/models/chat.py`:

```python
"""SQLAlchemy chat models"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship
from app.db.models.base import Base
import uuid
from datetime import datetime


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

### 3. Создать Pydantic схемы для API

Создать файл `backend/app/schemas/chat.py`:

```python
"""Chat Pydantic schemas (DTOs)"""
from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ConversationResponse(BaseModel):
    """Conversation response DTO"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    trip_id: UUID
    driver_id: UUID
    passenger_id: UUID
    created_at: datetime
    updated_at: datetime


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
```

## Критерии приёмки

- [ ] Файл `backend/app/models/chat.py` создан и содержит модели Conversation и Message
- [ ] Файл `backend/app/db/models/chat.py` создан и содержит SQLAlchemy модели с отношениями
- [ ] Файл `backend/app/schemas/chat.py` создан и содержит Pydantic схемы для API
- [ ] Все файлы соответствуют стилю кода проекта
- [ ] Типы данных UUID используются для всех ID