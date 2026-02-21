# Файловая структура проекта (Skeleton)

> Версия: 1.0 (MVP)
> Назначение: Список файлов для создания backend skeleton с in-memory storage

---

## Структура каталогов

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Точка входа приложения
│   │
│   ├── core/                      # Конфигурация и безопасность
│   │   ├── __init__.py
│   │   ├── config.py              # Настройки приложения
│   │   ├── security.py            # Пароли, JWT
│   │   └── database.py            # Инициализация storage
│   │
│   ├── models/                    # Domain models (Pydantic)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── trip.py
│   │   ├── request.py
│   │   └── notification.py
│   │
│   ├── repositories/              # Repository слой
│   │   ├── __init__.py
│   │   ├── interfaces.py         # ABC интерфейсы
│   │   ├── user_repo.py
│   │   ├── trip_repo.py
│   │   ├── request_repo.py
│   │   └── notification_repo.py
│   │
│   ├── services/                  # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── trip_service.py
│   │   ├── request_service.py
│   │   ├── notification_service.py
│   │   └── user_service.py
│   │
│   ├── api/                      # API endpoints
│   │   ├── __init__.py
│   │   ├── deps.py                # Зависимости (get_current_user)
│   │   ├── auth.py
│   │   ├── trips.py
│   │   ├── requests.py
│   │   ├── users.py
│   │   └── notifications.py
│   │
│   └── schemas/                   # Request/Response DTOs
│       ├── __init__.py
│       ├── user.py
│       ├── trip.py
│       ├── request.py
│       └── notification.py
│
├── tests/                         # Тесты
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_trips.py
│   └── test_requests.py
│
├── requirements.txt
├── .env                           # Переменные окружения
└── .gitignore
```

---

## Описание файлов

### `app/main.py`

```python
"""
Точка входа FastAPI приложения.
Инициализирует приложение, подключает роутеры, настраивает CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, trips, requests, users, notifications
from app.core.config import settings

app = FastAPI(
    title="Ride Sharing API",
    version="1.0.0",
    description="MVP API для поиска попутчиков"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(requests.router, prefix="/api/requests", tags=["requests"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

@app.get("/")
async def root():
    return {"message": "Ride Sharing API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

---

### `app/core/config.py`

```python
"""
Конфигурация приложения через переменные окружения.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # App
    APP_NAME: str = "Ride Sharing API"
    DEBUG: bool = True
    
    # JWT
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 часа
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Storage
    USE_POSTGRESQL: bool = False
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
```

---

### `app/core/security.py`

```python
"""
Функции для работы с безопасностью: пароли, JWT.
"""
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from uuid import UUID

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Хешировать пароль"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Создать JWT токен"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    """Декодировать токен"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None
```

---

### `app/core/database.py`

```python
"""
Инициализация in-memory storage.
"""
from app.repositories.user_repo import InMemoryUserRepository
from app.repositories.trip_repo import InMemoryTripRepository
from app.repositories.request_repo import InMemoryRequestRepository
from app.repositories.notification_repo import InMemoryNotificationRepository

class Database:
    def __init__(self):
        self.users = InMemoryUserRepository()
        self.trips = InMemoryTripRepository()
        self.requests = InMemoryRequestRepository()
        self.notifications = InMemoryNotificationRepository()

db = Database()

def get_db():
    return db
```

---

### `app/models/user.py`

```python
"""Domain models - User"""
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: UUID
    email: EmailStr
    password_hash: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
```

---

### `app/models/trip.py`

```python
"""Domain models - Trip"""
from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class Trip(BaseModel):
    id: UUID
    driver_id: UUID
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None
    status: str  # active, completed, cancelled
    created_at: datetime
    
    class Config:
        from_attributes = True
```

---

### `app/repositories/interfaces.py`

```python
"""Интерфейсы Repository (Abstract Base Classes)"""
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID
from app.models.user import User
from app.models.trip import Trip
from app.models.request import TripRequest
from app.models.notification import Notification

class IUserRepository(ABC):
    @abstractmethod
    async def create(self, user_data: dict) -> User: pass
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]: pass
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]: pass
    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]: pass

class ITripRepository(ABC):
    @abstractmethod
    async def create(self, trip_data: dict) -> Trip: pass
    @abstractmethod
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]: pass
    @abstractmethod
    async def update(self, trip_id: UUID, trip_data: dict) -> Optional[Trip]: pass
    @abstractmethod
    async def delete(self, trip_id: UUID) -> bool: pass
    @abstractmethod
    async def list_by_filters(self, from_city: str, to_city: str, date: Optional[str], status: str) -> list[Trip]: pass
    @abstractmethod
    async def list_by_driver(self, driver_id: UUID) -> list[Trip]: pass

class IRequestRepository(ABC):
    @abstractmethod
    async def create(self, request_data: dict) -> TripRequest: pass
    @abstractmethod
    async def get_by_id(self, request_id: UUID) -> Optional[TripRequest]: pass
    @abstractmethod
    async def get_by_trip(self, trip_id: UUID) -> list[TripRequest]: pass
    @abstractmethod
    async def get_by_passenger(self, passenger_id: UUID) -> list[TripRequest]: pass
    @abstractmethod
    async def update_status(self, request_id: UUID, status: str) -> Optional[TripRequest]: pass
    @abstractmethod
    async def exists(self, trip_id: UUID, passenger_id: UUID) -> bool: pass

class INotificationRepository(ABC):
    @abstractmethod
    async def create(self, notification_data: dict) -> Notification: pass
    @abstractmethod
    async def get_by_user(self, user_id: UUID, is_read: Optional[bool]) -> list[Notification]: pass
    @abstractmethod
    async def mark_as_read(self, notification_id: UUID) -> Optional[Notification]: pass
    @abstractmethod
    async def mark_all_as_read(self, user_id: UUID) -> int: pass
```

---

### `app/repositories/user_repo.py`

```python
"""In-memory User Repository"""
from uuid import UUID, uuid4
from typing import Optional
from datetime import datetime

from app.models.user import User
from app.repositories.interfaces import IUserRepository

class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self._users: dict[UUID, User] = {}
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
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._users.get(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        user_id = self._email_index.get(email)
        return self._users.get(user_id) if user_id else None
    
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        if user_id not in self._users:
            return None
        user = self._users[user_id]
        for key, value in user_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        return user
```

---

### `app/api/deps.py`

```python
"""Зависимости для API endpoints"""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.core.security import decode_token

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """Получить текущего пользователя из токена"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    db = get_db()
    user = await db.users.get_by_id(UUID(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
```

---

### `app/api/auth.py`

```python
"""Auth endpoints"""
from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter()

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/register")
async def register(request: RegisterRequest):
    db = get_db()
    
    # Проверка email
    existing = await db.users.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Создание пользователя
    user = await db.users.create({
        "email": request.email,
        "password_hash": get_password_hash(request.password),
        "name": request.name,
        "phone": request.phone
    })
    
    # Генерация токена
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name
    })
    
    response = Response(status_code=status.HTTP_201_CREATED)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=86400
    )
    
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "phone": user.phone
    }

@router.post("/login")
async def login(request: LoginRequest, response: Response):
    db = get_db()
    
    user = await db.users.get_by_email(request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name
    })
    
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age=86400
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone
        }
    }

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"message": "Logged out"}

@router.get("/me")
async def get_me(current_user = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "rating": current_user.rating,
        "created_at": current_user.created_at.isoformat()
    }
```

---

### `requirements.txt`

```
fastapi==0.109.0
uvicorn==0.27.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
pydantic==2.5.3
pydantic-settings==2.1.0
python-multipart==0.0.6
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0
```

---

## Быстрый старт

```bash
# 1. Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 2. Установить зависимости
pip install -r requirements.txt

# 3. Запустить сервер
uvicorn app.main:app --reload

# 4. Проверить работу
curl http://localhost:8000/health
```

## Следующие шаги

1. [ ] Реализовать остальные endpoints (trips, requests, users, notifications)
2. [ ] Написать unit тесты
3. [ ] Интегрировать с frontend
4. [ ] Добавить PostgreSQL через SQLAlchemy
