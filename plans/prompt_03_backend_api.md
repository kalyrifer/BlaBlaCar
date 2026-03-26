# Промпт 3: Backend — API эндпоинты чата

## Задача

Создать API роутер для системы чата в проекте RoadMate.

## Требования к проекту

- Проект: RoadMate — веб-приложение для карпулинга на FastAPI
- Уже созданы: модели, репозиторий, сервис из промптов 1 и 2
- Стиль API: используется `Depends(get_current_user)` для аутентификации

## Справочная информация

Пример существующего API эндпоинта:

```python
# backend/app/api/users.py
from fastapi import APIRouter, HTTPException, Depends
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {"id": str(current_user.id), "name": current_user.name}
```

Пример подключения роутера в main.py:

```python
# backend/app/main.py
from app.api.users import router as users_router
app.include_router(users_router, prefix="/api/users", tags=["users"])
```

## Задание

### Создать API роутер чата

Создать файл `backend/app/api/chat.py`:

```python
"""Chat API endpoints"""
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import MessageResponse, ConversationListItem
from app.services.chat_service import ChatService
from app.core.database import get_db


router = APIRouter()


class SendMessageRequest(BaseModel):
    """Request to send a message"""
    content: str


def get_chat_service() -> ChatService:
    """Get chat service instance"""
    from app.repositories.inmemory.chat_repo import InMemoryChatRepository
    repo = InMemoryChatRepository()
    return ChatService(repo)


@router.get("/conversations", response_model=list[ConversationListItem])
async def get_my_conversations(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Get all conversations for current user"""
    from app.repositories.inmemory.trip_repo import InMemoryTripRepository
    from app.repositories.inmemory.user_repo import InMemoryUserRepository
    
    # Get repositories from database
    db = get_db()
    trip_repo = db.trips
    user_repo = db.users
    
    return await chat_service.get_user_conversations(
        current_user.id,
        trip_repo,
        user_repo
    )


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
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
    chat_service: ChatService = Depends(get_chat_service)
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
        from app.domain.enums import RequestStatus
        confirmed_requests = [r for r in requests if r.status == RequestStatus.CONFIRMED]
        
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
        from app.domain.enums import RequestStatus
        trip_request = next(
            (r for r in requests if r.trip_id == trip_uuid and r.status == RequestStatus.CONFIRMED),
            None
        )
        
        if not trip_request:
            raise HTTPException(
                status_code=403,
                detail="You don't have a confirmed request for this trip"
            )
        
        passenger_id = current_user.id
    
    # Get or create conversation
    chat_service = get_chat_service()
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

### Подключить роутер в main.py

Добавить в `backend/app/main.py`:

```python
# В начале файла, с другими импортами
from app.api.chat import router as chat_router

# В функции create_app() или в конце функции, после других роутеров
app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
```

## Критерии приёмки

- [ ] Файл `backend/app/api/chat.py` создан с четырьмя эндпоинтами
- [ ] Эндпоинт `GET /conversations` возвращает список чатов текущего пользователя
- [ ] Эндпоинт `GET /conversations/{id}/messages` возвращает сообщения с пагинацией
- [ ] Эндпоинт `POST /conversations/{id}/messages` позволяет отправить сообщение
- [ ] Эндпоинт `POST /trips/{id}/conversation` создаёт чат для подтверждённой поездки
- [ ] Все эндпоинты требуют аутентификации (Depends(get_current_user))
- [ ] Роутер подключён в main.py с префиксом `/api/chat`