# RoadMate - BlaBlaCar Clone

## Общее описание

Веб-приложение для поиска попутчиков (аналог BlaBlaCar). Позволяет водителям создавать поездки, а пассажирам - находить и бронировать места.

## Технологический стек

### Backend
- **Framework**: FastAPI (Python)
- **Authentication**: JWT токены
- **Password Hashing**: bcrypt через passlib
- **Validation**: Pydantic v2
- **Storage**: In-memory база данных (Mock)
- **Port**: 8000

### Frontend
- **Framework**: React 18
- **Language**: TypeScript
- **Build Tool**: Vite
- **Routing**: React Router DOM v6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Styling**: CSS (custom)
- **Port**: 5174

---

## Архитектура проекта

```
BlaBlaCar/
├── backend/
│   └── app/
│       ├── api/           # API endpoints
│       ├── core/         # Конфигурация, безопасность, БД
│       ├── models/       # Pydantic модели
│       ├── repositories/ # Data access layer
│       └── schemas/      # Схемы (пусто)
│
└── frontend/
    └── src/
        ├── components/   # React компоненты
        ├── pages/       # Страницы
        ├── services/    # API клиент
        ├── stores/      # Zustand стейты
        └── types/      # TypeScript типы
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

### Trips (`/api/trips`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/` | Создать поездку |
| GET | `/` | Поиск поездок (фильтры: from_city, to_city, date) |
| GET | `/my/driver` | Мои поездки как водитель |
| GET | `/{trip_id}` | Получить поездку по ID |
| PUT | `/{trip_id}` | Обновить поездку |
| DELETE | `/{trip_id}` | Удалить поездку |
| POST | `/{trip_id}/requests` | Создать заявку на поездку |
| GET | `/{trip_id}/requests` | Получить заявки к поездке (только водитель) |

### Requests (`/api/requests`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/my` | Мои заявки как пассажир |
| PUT | `/{request_id}` | Обновить статус заявки (подтвердить/отклонить) |

### Users (`/api/users`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{user_id}` | Получить профиль пользователя |
| PUT | `/{user_id}` | Обновить профиль |
| GET | `/{user_id}/trips` | Получить поездки пользователя |

### Notifications (`/api/notifications`)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Получить уведомления |
| PUT | `/{notification_id}/read` | Отметить уведомление как прочитанное |
| PUT | `/read-all` | Отметить все как прочитанные |

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
- rating: Optional[float]
- created_at: datetime
```

### Trip
```
- id: UUID
- driver_id: UUID
- from_city: str
- to_city: str
- departure_date: str (YYYY-MM-DD)
- departure_time: str (HH:MM)
- available_seats: int
- price_per_seat: int
- description: Optional[str]
- status: active | completed | cancelled
- created_at: datetime
```

### TripRequest
```
- id: UUID
- trip_id: UUID
- passenger_id: UUID
- seats_requested: int
- message: Optional[str]
- status: pending | confirmed | rejected
- created_at: datetime
- updated_at: Optional[datetime]
```

### Notification
```
- id: UUID
- user_id: UUID
- type: request_received | request_confirmed | request_rejected | trip_cancelled
- title: str
- message: str
- is_read: bool
- related_trip_id: Optional[UUID]
- related_request_id: Optional[UUID]
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
2. **MyTripsPage** (`/my-trips`) - Мои поездки как водитель
3. **NotificationsPage** (`/notifications`) - Уведомления

---

## Репозитории (In-Memory Storage)

- **UserRepository** - управление пользователями
- **TripRepository** - управление поездками
- **RequestRepository** - управление заявками
- **NotificationRepository** - управление уведомлениями

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
npm run dev
```

---

## Текущий статус

Приложение находится в рабочем состоянии:
- Backend запущен на http://localhost:8000
- Frontend запущен на http://localhost:5174
- API документация доступна по адресу http://localhost:8000/docs

### Реализованные функции
- Регистрация и аутентификация пользователей
- Поиск поездок по городу отправления, прибытия и дате
- Создание поездок водителями
- Бронирование мест пассажирами
- Подтверждение/отклонение заявок водителями
- Уведомления о новых заявках и их статусе
- Просмотр профиля пользователя

### Что можно улучшить
- Заменить in-memory storage на реальную базу данных (PostgreSQL)
- Добавить загрузку аватаров
- Добавить систему рейтинга и отзывов
- Добавить чат между пользователями
- Добавить более продвинутые фильтры поиска
- Добавить админ-панель
