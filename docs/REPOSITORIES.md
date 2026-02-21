# Repository интерфейсы (In-Memory Storage)

> Версия: 1.0 (MVP)
> Назначение: Контракты для repository слоя с in-memory реализацией

## 1. Архитектура Repository слоя

```
┌─────────────────────────────────────────────────────────┐
│                     API Layer                            │
│  (endpoints/routers)                                    │
└─────────────────────┬───────────────────────────────────┘
                      │ Pydantic Schemas
┌─────────────────────▼───────────────────────────────────┐
│                   Service Layer                          │
│  (services)                                             │
└─────────────────────┬───────────────────────────────────┘
                      │ Domain Models
┌─────────────────────▼───────────────────────────────────┐
│                Repository Layer                          │
│  ┌─────────────────────────────────────────────────────┐│
│  │ IUserRepository / InMemoryUserRepository           ││
│  │ ITripRepository / InMemoryTripRepository           ││
│  │ IRequestRepository / InMemoryRequestRepository     ││
│  │ INotificationRepository / InMemoryNotificationRepo  ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

## 2. User Repository

### Интерфейс

```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

class IUserRepository(ABC):
    """Интерфейс репозитория пользователей"""
    
    @abstractmethod
    async def create(self, user_data: dict) -> User:
        """Создать пользователя"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Получить пользователя по ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        pass
    
    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Обновить данные пользователя"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Удалить пользователя"""
        pass
    
    @abstractmethod
    async def list_all(self) -> list[User]:
        """Получить всех пользователей"""
        pass
```

### In-Memory реализация

```python
from typing import Optional
from uuid import UUID, uuid4

class InMemoryUserRepository(IUserRepository):
    """In-memory реализация UserRepository"""
    
    def __init__(self):
        self._users: dict[UUID, dict] = {}
        self._email_index: dict[str, UUID] = {}
    
    async def create(self, user_data: dict) -> User:
        user_id = uuid4()
        user = User(
            id=user_id,
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            name=user_data["name"],
            phone=user_data.get("phone"),
            created_at=datetime.utcnow()
        )
        self._users[user_id] = user
        self._email_index[user.email] = user_id
        return user
```

---

## 3. Trip Repository

### Интерфейс

```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

class ITripRepository(ABC):
    """Интерфейс репозитория поездок"""
    
    @abstractmethod
    async def create(self, trip_data: dict) -> Trip:
        """Создать поездку"""
        pass
    
    @abstractmethod
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """Получить поездку по ID"""
        pass
    
    @abstractmethod
    async def update(self, trip_id: UUID, trip_data: dict) -> Optional[Trip]:
        """Обновить поездку"""
        pass
    
    @abstractmethod
    async def delete(self, trip_id: UUID) -> bool:
        """Удалить поездку"""
        pass
    
    @abstractmethod
    async def list_by_filters(
        self,
        from_city: str,
        to_city: str,
        date: Optional[str] = None,
        status: str = "active"
    ) -> list[Trip]:
        """Поиск поездок по фильтрам"""
        pass
    
    @abstractmethod
    async def list_by_driver(self, driver_id: UUID) -> list[Trip]:
        """Получить поездки водителя"""
        pass
    
    @abstractmethod
    async def update_seats(self, trip_id: UUID, seats_delta: int) -> Optional[Trip]:
        """Обновить количество мест"""
        pass
```

### In-Memory реализация

```python
class InMemoryTripRepository(ITripRepository):
    """In-memory реализация TripRepository"""
    
    def __init__(self):
        self._trips: dict[UUID, dict] = {}
    
    async def list_by_filters(
        self,
        from_city: str,
        to_city: str,
        date: Optional[str] = None,
        status: str = "active"
    ) -> list[Trip]:
        results = []
        for trip in self._trips.values():
            if (trip["from_city"] == from_city and
                trip["to_city"] == to_city and
                trip["status"] == status):
                if date is None or trip["departure_date"] == date:
                    results.append(trip)
        return results
```

---

## 4. Request Repository (Заявки)

### Интерфейс

```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

class IRequestRepository(ABC):
    """Интерфейс репозитория заявок"""
    
    @abstractmethod
    async def create(self, request_data: dict) -> TripRequest:
        """Создать заявку"""
        pass
    
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[TripRequest]:
        """Получить заявку по ID"""
        pass
    
    @abstractmethod
    async def get_by_trip(self, trip_id: UUID) -> list[TripRequest]:
        """Получить заявки на поездку"""
        pass
    
    @abstractmethod
    async def get_by_passenger(self, passenger_id: UUID) -> list[TripRequest]:
        """Получить заявки пассажира"""
        pass
    
    @abstractmethod
    async def update_status(
        self,
        request_id: UUID,
        status: str
    ) -> Optional[TripRequest]:
        """Обновить статус заявки"""
        pass
    
    @abstractmethod
    async def exists(
        self,
        trip_id: UUID,
        passenger_id: UUID
    ) -> bool:
        """Проверить, существует ли заявка"""
        pass
```

---

## 5. Notification Repository

### Интерфейс

```python
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

class INotificationRepository(ABC):
    """Интерфейс репозитория уведомлений"""
    
    @abstractmethod
    async def create(self, notification_data: dict) -> Notification:
        """Создать уведомление"""
        pass
    
    @abstractmethod
    async def get_by_id(self, notification_id: UUID) -> Optional[Notification]:
        """Получить уведомление по ID"""
        pass
    
    @abstractmethod
    async def get_by_user(
        self,
        user_id: UUID,
        is_read: Optional[bool] = None
    ) -> list[Notification]:
        """Получить уведомления пользователя"""
        pass
    
    @abstractmethod
    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]:
        """Отметить как прочитанное"""
        pass
    
    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int:
        """Отметить все как прочитанные"""
        pass
    
    @abstractmethod
    async def get_unread_count(self, user_id: UUID) -> int:
        """Получить количество непрочитанных"""
        pass
```

---

## 6. Domain Models

```python
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: UUID
    email: str
    password_hash: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

class Trip(BaseModel):
    id: UUID
    driver_id: UUID
    from_city: str
    to_city: str
    departure_date: str  # YYYY-MM-DD
    departure_time: str  # HH:MM
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str  # active, completed, cancelled
    created_at: datetime

class TripRequest(BaseModel):
    id: UUID
    trip_id: UUID
    passenger_id: UUID
    seats_requested: int
    message: Optional[str] = None
    status: str  # pending, confirmed, rejected
    created_at: datetime
    updated_at: Optional[datetime] = None

class Notification(BaseModel):
    id: UUID
    user_id: UUID
    type: str  # request_received, request_confirmed, etc.
    title: str
    message: str
    is_read: bool = False
    related_trip_id: Optional[UUID] = None
    related_request_id: Optional[UUID] = None
    created_at: datetime
```

---

## 7. Использование в Service слое

```python
class TripService:
    def __init__(self, trip_repo: ITripRepository):
        self._trip_repo = trip_repo
    
    async def create_trip(self, trip_data: dict, driver_id: UUID) -> Trip:
        # Валидация данных
        # Бизнес-логика
        # Сохранение через repository
        return await self._trip_repo.create({
            **trip_data,
            "driver_id": driver_id,
            "status": "active"
        })
```

---

## 8. Переключение на PostgreSQL

Для подключения PostgreSQL достаточно заменить реализацию:

```python
# Внедрение зависимости
def get_trip_repository() -> ITripRepository:
    if settings.USE_POSTGRESQL:
        return PostgresTripRepository()
    return InMemoryTripRepository()

# Или через DI контейнер
container.register(ITripRepository, PostgresTripRepository)
```

### Postgres реализация (будущая)

```python
class PostgresTripRepository(ITripRepository):
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def create(self, trip_data: dict) -> Trip:
        # SQLAlchemy код
        pass
```

---

## 9. Тестирование

### Unit тесты с mock

```python
import pytest
from unittest.mock import AsyncMock

@pytest.fixture
def mock_user_repo():
    repo = AsyncMock(spec=IUserRepository)
    repo.get_by_email.return_value = None
    return repo

@pytest.mark.asyncio
async def test_create_user(mock_user_repo):
    mock_user_repo.create.return_value = User(...)
    
    result = await mock_user_repo.create({
        "email": "test@example.com",
        "password_hash": "hash",
        "name": "Test"
    })
    
    assert result.email == "test@example.com"
    mock_user_repo.create.assert_called_once()
```

### Integration тесты

```python
@pytest.fixture
async def in_memory_app():
    """Приложение с in-memory storage для тестов"""
    app = FastAPI()
    app.include_router(router)
    # Подключение in-memory repositories
    return app
```
