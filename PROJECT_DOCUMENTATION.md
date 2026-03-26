# RoadMate - Техническая документация

## Общее описание

Веб-приложение для поиска попутчиков (аналог BlaBlaCar). Позволяет водителям создавать поездки, а пассажирам - находить и бронировать места.

## Технологический стек

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: JWT токены
- **Password Hashing**: bcrypt через passlib
- **Validation**: Pydantic v2
- **Storage**: In-memory база данных (по умолчанию) или PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Port**: 8000

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: React Router DOM v6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Styling**: CSS (custom)
- **Port**: 5173

---

## Архитектура проекта

```
BlaBlaCar/
├── backend/
│   └── app/
│       ├── api/           # API endpoints
│       ├── core/          # Конфигурация, безопасность, БД
│       ├── models/        # Pydantic модели
│       ├── repositories/ # Data access layer
│       │   ├── interfaces/  # Абстрактные интерфейсы
│       │   └── inmemory/    # In-memory реализации
│       ├── services/      # Бизнес-логика
│       ├── schemas/       # Pydantic схемы
│       ├── domain/        # Доменные модели и enums
│       ├── db/            # SQLAlchemy модели
│       │   ├── models/
│       │   └── repositories/  # PostgreSQL репозитории
│       ├── background/   # Фоновые задачи
│       ├── utils/         # Утилиты
│       └── main.py        # Точка входа
│
└── frontend/
    └── src/
        ├── components/    # React компоненты
        │   ├── ui/        # Базовые UI компоненты
        │   ├── chat/     # Чат компоненты
        │   └── Layout.tsx
        ├── pages/        # Страницы
        ├── services/     # API клиент
        ├── stores/       # Zustand стейты
        └── types/        # TypeScript типы
```

---

## API Endpoints

### Auth (`/api/auth`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/register` | Регистрация нового пользователя |
| POST | `/login` | Вход в систему |
| POST | `/logout` | Выход из системы |
| GET | `/me` | Получить данные текущего пользователя |
| POST | `/refresh` | Обновление токена |

### Trips (`/api/trips`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Создать поездку |
| GET | `/` | Поиск поездок (фильтры: origin, destination, date) |
| GET | `/my/driver` | Мои поездки как водитель |
| GET | `/{trip_id}` | Получить поездку по ID |
| PUT | `/{trip_id}` | Обновить поездку |
| DELETE | `/{trip_id}` | Удалить поездку |

### Requests (`/api/requests`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/trips/{trip_id}/requests` | Создать заявку на поездку |
| GET | `/my` | Мои заявки как пассажир |
| GET | `/trips/{trip_id}/requests` | Получить заявки к поездке (только водитель) |
| PUT | `/{request_id}` | Обновить статус заявки (подтвердить/отклонить) |

### Users (`/api/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{user_id}` | Получить профиль пользователя |
| PUT | `/{user_id}` | Обновить профиль |
| GET | `/{user_id}/trips` | Получить поездки пользователя |
| GET | `/{user_id}/reviews` | Получить отзывы о пользователе |

### Notifications (`/api/notifications`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Получить уведомления |
| PUT | `/{notification_id}/read` | Отметить уведомление как прочитанное |
| PUT | `/read-all` | Отметить все как прочитанные |

### Chat (`/api/chats`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Получить список чатов |
| POST | `/` | Создать чат |
| GET | `/{chat_id}` | Получить чат с сообщениями |
| POST | `/{chat_id}/messages` | Отправить сообщение |

### Reviews (`/api/reviews`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Создать отзыв |
| GET | `/user/{user_id}` | Получить отзывы о пользователе |

---

## Модели данных

### User
```
- id: UUID
- email: EmailStr
- password_hash: str
- name: str
- phone: Optional[str]
- avatar_url: Optional[str]
- rating: float (средний рейтинг)
- created_at: datetime
- updated_at: datetime
```

### Trip
```
- id: UUID
- driver_id: UUID
- origin: str
- destination: str
- departure_time: datetime
- available_seats: int
- price: float
- status: ACTIVE | COMPLETED | CANCELLED
- description: Optional[str]
- created_at: datetime
- updated_at: datetime
```

### TripRequest
```
- id: UUID
- trip_id: UUID
- passenger_id: UUID
- seats_requested: int
- message: Optional[str]
- status: PENDING | APPROVED | REJECTED | CANCELLED
- created_at: datetime
- updated_at: Optional[datetime]
```

### Notification
```
- id: UUID
- user_id: UUID
- type: NEW_REQUEST | REQUEST_APPROVED | REQUEST_REJECTED | TRIP_CANCELLED | REQUEST_CANCELLED | NEW_MESSAGE | NEW_REVIEW
- title: str
- message: str
- is_read: bool
- related_trip_id: Optional[UUID]
- related_request_id: Optional[UUID]
- created_at: datetime
```

### Chat
```
- id: UUID
- trip_id: Optional[UUID]
- participants: list[UUID]
- created_at: datetime
- updated_at: datetime
```

### Message
```
- id: UUID
- chat_id: UUID
- sender_id: UUID
- content: str
- created_at: datetime
- is_read: bool
```

### Review
```
- id: UUID
- author_id: UUID
- target_id: UUID
- trip_id: UUID
- rating: int (1-5)
- comment: Optional[str]
- review_type: DRIVER_TO_PASSENGER | PASSENGER_TO_DRIVER
- created_at: datetime
```

---

## Frontend Страницы

### Public страницы
1. **HomePage** (`/`) - Главная страница с поиском и информацией о сервисе
2. **TripsPage** (`/trips`) - Результаты поиска поездок
3. **TripPage** (`/trips/:id`) - Детали поездки
4. **LoginPage** (`/login`) - Форма входа
5. **RegisterPage** (`/register`) - Форма регистрации
6. **ProfilePage** (`/profile/:id?`) - Профиль пользователя

### Protected страницы (требуют авторизации)
1. **CreateTripPage** (`/trips/new`) - Создание новой поездки
2. **MyTripsPage** (`/trips/my`) - Мои поездки как водитель
3. **NotificationsPage** (`/notifications`) - Уведомления
4. **MessagesPage** (`/messages`) - Список чатов
5. **ChatPage** (`/messages/:chatId`) - Чат с сообщениями

---

## Конфигурация

### Переменные окружения (.env)

```env
# Настройки приложения
APP_NAME=Ride Sharing API
DEBUG=True

# Настройки JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# База данных
USE_POSTGRESQL=False

# PostgreSQL (если USE_POSTGRESQL=True)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=blablacar
```

---

## Репозитории

### In-Memory хранилище (по умолчанию)
- **UserRepository** - управление пользователями
- **TripRepository** - управление поездками
- **RequestRepository** - управление заявками
- **NotificationRepository** - управление уведомлениями
- **ChatRepository** - управление чатами и сообщениями
- **ReviewRepository** - управление отзывами

### PostgreSQL хранилище (опционально)
- Аналогичные репозитории для работы с PostgreSQL
- Требует настройки USE_POSTGRESQL=True

---

## Безопасность

### JWT Аутентификация
- Access токены истекают через 24 часа (настраивается)
- Refresh токены для автоматического обновления
- Токены передаются в заголовке `Authorization: Bearer <token>`

### Защита паролей
- Используется bcrypt для хэширования
- Пароли никогда не хранятся в открытом виде

### CORS
- По умолчанию разрешены localhost:5173 (frontend) и localhost:3000
- Настраивается через ALLOWED_ORIGINS

---

## Запуск проекта

### Backend
```bash
cd backend
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Текущий статус

Приложение находится в рабочем состоянии:
- Backend запущен на http://localhost:8000
- Frontend запущен на http://localhost:5173
- API документация доступна по адресу http://localhost:8000/docs

### Реализованные функции
✓ Регистрация и аутентификация пользователей
✓ Поиск поездок по городу отправления, прибытия и дате
✓ Создание поездок водителями
✓ Бронирование мест пассажирами
✓ Подтверждение/отклонение заявок водителями
✓ Уведомления о новых заявках и их статусе
✓ Просмотр профиля пользователя
✓ Система чатов между пользователями
✓ Система отзывов и рейтинга

### Что можно улучшить
- Заменить in-memory storage на PostgreSQL для production
- Добавить загрузку аватаров
- Добавить push-уведомления
- Добавить email уведомления
- Добавить админ-панель
- Добавить интеграцию с картами (Google Maps, Yandex Maps)
- Добавить оплату внутри приложения

---

## Архитектурные особенности

### Clean Architecture
Проект следует принципам чистой архитектуры с чётким разделением на слои:
- API Layer - обработка HTTP запросов
- Service Layer - бизнес-логика
- Repository Layer - абстракция доступа к данным
- Domain Layer - доменные модели

### Паттерн Репозиторий
Позволяет легко переключаться между In-memory и PostgreSQL хранилищами без изменения бизнес-логики.

### Параллелизм
Использование asyncio.Lock для обработки параллельных заявок на поездку, предотвращая race condition.
