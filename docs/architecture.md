# Архитектура MVP — Приложение для поиска попутчиков

## 1. High-Level Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                            FRONTEND LAYER                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SPA (Single Page Application)                  │   │
│  │  • React / Vue.js / Svelte                                       │   │
│  │  • Mobile-first адаптивный интерфейс                              │   │
│  │  • PWA готовность (опционально)                                   │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ HTTP/REST + JSON
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            BACKEND LAYER                                 │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      FastAPI Application                         │   │
│  │  • Auth Service (регистрация, вход, JWT токены)                   │   │
│  │  • Trip Service (создание, поиск, управление поездками)           │   │
│  │  • Request Service (заявки пассажиров, подтверждение водителем)  │   │
│  │  • Notification Service (in-app уведомления)                      │   │
│  │  • User Service (профиль, история поездок)                        │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ SQLAlchemy ORM
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           DATABASE LAYER                                │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                    SQLite (MVP) → PostgreSQL (prod)              │   │
│  │                                                                   │   │
│  │  • users (пользователи)                                         │   │
│  │  • trips (поездки)                                              │   │
│  │  • trip_requests (заявки)                                       │   │
│  │  • notifications (уведомления)                                  │   │
│  └──────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

## 2. Детали архитектуры

### 2.1 Frontend

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Фреймворк | React / Vue.js 3 | SPA с реактивным UI |
| Стили | Tailwind CSS / Styled Components | Адаптивный mobile-first дизайн |
| HTTP клиент | Axios / Fetch API | Коммуникация с backend |
| Состояние | React Context / Vue Pinia | Управление состоянием приложения |

**Страницы:**
- Главная (форма поиска)
- Результаты поиска
- Карточка поездки
- Создание поездки
- Профиль пользователя
- Мои поездки (водитель/пассажир)

### 2.2 Backend

| Компонент | Технология | Назначение |
|-----------|------------|------------|
| Web-фреймворк | FastAPI | ASGI веб-фреймворк |
| ORM | SQLAlchemy 2.0 | Работа с базой данных |
| Валидация | Pydantic v2 | DTO и валидация данных |
| Аутентификация | JWT (python-jose) | Токенная авторизация |
| Миграции | Alembic | Управление схемой БД |

**API Endpoints:**

```
AUTH:
POST   /api/auth/register      # Регистрация
POST   /api/auth/login         # Вход (возвращает JWT)
GET    /api/auth/me            # Текущий пользователь

TRIPS:
POST   /api/trips               # Создать поездку (водитель)
GET    /api/trips               # Поиск поездок (фильтры: from, to, date)
GET    /api/trips/{id}          # Детали поездки
PUT    /api/trips/{id}          # Обновить поездку
DELETE /api/trips/{id}          # Удалить поездку

REQUESTS:
POST   /api/trips/{id}/request  # Отправить заявку (пассажир)
GET    /api/requests            # Мои заявки (пассажир)
GET    /api/trips/{id}/requests # Заявки на поездку (водитель)
PUT    /api/requests/{id}       # Подтвердить/отклонить заявку

NOTIFICATIONS:
GET    /api/notifications       # Список уведомлений
PUT    /api/notifications/{id}/read  # Прочитано

USERS:
GET    /api/users/{id}          # Профиль пользователя
PUT    /api/users/{id}          # Обновить профиль
GET    /api/users/{id}/trips    # Поездки пользователя
```

### 2.3 База данных

**Схема таблиц:**

```sql
-- users (пользователи)
id, email, password_hash, name, phone, 
avatar_url, rating, created_at, updated_at

-- trips (поездки)
id, driver_id, from_city, to_city, 
departure_date, departure_time, 
available_seats, price_per_seat, 
description, status, created_at, updated_at

-- trip_requests (заявки)
id, trip_id, passenger_id, seats_requested,
status (pending/confirmed/rejected), 
created_at, updated_at

-- notifications (уведомления)
id, user_id, type, title, message, 
is_read, related_trip_id, related_request_id,
created_at
```

## 3. Коммуникация между компонентами

### 3.1 Форматы данных

| Направление | Формат | Примечание |
|-------------|--------|------------|
| Frontend → Backend | JSON over HTTP | REST API |
| Backend → Frontend | JSON | Ответы API |
| Аутентификация | JWT Bearer Token | В заголовке Authorization |

### 3.2 Типичные запросы/ответы

**Создание поездки (POST /api/trips):**
```json
Request:
{
  "from_city": "Москва",
  "to_city": "Санкт-Петербург",
  "departure_date": "2024-03-15",
  "departure_time": "10:00",
  "available_seats": 3,
  "price_per_seat": 1500,
  "description": "Комфортная поездка, остановки по желанию"
}

Response:
{
  "id": "uuid",
  "driver_id": "uuid",
  "from_city": "Москва",
  "to_city": "Санкт-Петербург",
  "departure_date": "2024-03-15",
  "departure_time": "10:00",
  "available_seats": 3,
  "price_per_seat": 1500,
  "status": "active",
  "created_at": "2024-03-01T10:00:00Z"
}
```

**Поиск поездок (GET /api/trips):**
```
GET /api/trips?from_city=Москва&to_city=Санкт-Петербург&date=2024-03-15
```

## 4. Сервисы для локального запуска

Для разработки необходимо запустить:

1. **Backend API** — `uvicorn main:app --reload`
   - Порт: 8000
   - Документация: http://localhost:8000/docs

2. **Frontend Dev Server** — `npm run dev` / `vite`
   - Порт: 5173 (Vite) или 3000 (CRA)
   - Проксирует API запросы на backend

3. **База данных** — SQLite файл (автоматически создаётся)
   - Путь: `./data/app.db`

## 5. Структура проекта

```
/project-root
├── backend/
│   ├── app/
│   │   ├── api/           # API роутеры
│   │   │   ├── auth.py
│   │   │   ├── trips.py
│   │   │   ├── requests.py
│   │   │   ├── users.py
│   │   │   └── notifications.py
│   │   ├── core/          # Конфигурация
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── database.py
│   │   ├── models/        # SQLAlchemy модели
│   │   │   ├── user.py
│   │   │   ├── trip.py
│   │   │   └── notification.py
│   │   ├── schemas/       # Pydantic схемы
│   │   │   ├── user.py
│   │   │   ├── trip.py
│   │   │   └── ...
│   │   └── main.py        # Точка входа
│   ├── alembic/           # Миграции
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/    # UI компоненты
│   │   ├── pages/         # Страницы
│   │   ├── services/      # API клиент
│   │   ├── stores/        # Состояние
│   │   ├── App.vue / App.tsx
│   │   └── main.ts / main.jsx
│   ├── package.json
│   └── vite.config.ts
│
└── docker-compose.yml     # Опционально для prod
```

## 6. Принятые архитектурные решения

| Решение | Обоснование |
|---------|-------------|
| FastAPI | Высокая производительность, auto-documentation, async support |
| SQLite → PostgreSQL | Простота для MVP, легкая миграция в prod |
| JWT аутентификация | Stateless, масштабируемость, стандарт |
| REST API | Простота, широкое использование, понятный API |
| Pydantic v2 + SQLAlchemy 2.0 | Современные версии с улучшенной производительностью |

## 7. Roadmap для следующих этапов

- [ ] Этап 2: Реализация backend (модели, API endpoints)
- [ ] Этап 3: Реализация frontend (компоненты, страницы)
- [ ] Этап 4: Тестирование и интеграция
- [ ] Этап 5: PostgreSQL миграция для production
