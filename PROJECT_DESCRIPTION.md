# RoadMate — Подробное описание проекта

## Содержание

1. [Введение](#введение)
2. [Основные возможности](#основные-возможности)
3. [Архитектура системы](#архитектура-системы)
4. [Структура проекта](#структура-проекта)
5. [Технологический стек](#технологический-стек)
6. [Модели данных](#модели-данных)
7. [API эндпоинты](#api-эндпоинты)
8. [Бизнес-логика](#бизнес-логика)
9. [Система уведомлений](#система-уведомлений)
10. [Система чатов](#система-чатов)
11. [Система отзывов](#система-отзывов)
12. [Безопасность](#безопасность)
13. [Тестирование](#тестирование)
14. [Конкурентность и блокировки](#конкурентность-и-блокировки)
15. [Конфигурация](#конфигурация)
16. [Запуск и разработка](#запуск-и-разработка)

---

## Введение

**RoadMate** — это полноценное веб-приложение для поиска и организации совместных поездок (карпулинга), аналог популярного сервиса BlaBlaCar. Проект разработан с использованием современных технологий и следует принципам чистой архитектуры.

### Назначение проекта

Платформа позволяет водителям создавать поездки из одного города в другой, а пассажирам — находить и бронировать места в этих поездках. Это обеспечивает удобный и экономически выгодный способ перемещения между городами.

### Ключевые характеристики

- **Полный цикл:** от поиска поездки до завершения поездки
- **Асинхронная обработка:** использование FastAPI и фоновых воркеров
- **База данных:** PostgreSQL с async драйвером (sqlalchemy + asyncpg) или In-memory хранилище
- **Безопасность:** JWT аутентификация, хэширование паролей
- **Масштабируемость:** паттерн репозитория для абстракции данных
- **Тестируемость:** комплексное покрытие тестами
- **Чат:** встроенная система обмена сообщениями между пользователями
- **Отзывы:** система рейтинга и отзывов о пользователях

---

## Основные возможности

### 1. Аутентификация и авторизация

- **Регистрация пользователей** — создание аккаунта с email и паролем
- **Вход в систему** — получение JWT токенов доступа
- **Refresh токены** — автоматическое обновление истёкших токенов
- **Защищённые маршруты** — доступ к API только для авторизованных пользователей
- **Хэширование паролей** — безопасное хранение учётных данных с использованием bcrypt

### 2. Управление поездками (Trips)

Водители могут:

- Создавать новые поездки с указанием:
  - Маршрута (город отправления и прибытия)
  - Даты и времени отправления
  - Количества доступных мест
  - Цены за место
  - Дополнительной информации (остановки, условия)
- Просматривать свои поездки
- Редактировать детали поездки
- Отменять поездки
- Завершать поездки

Пассажиры могут:

- Искать поездки по:
  - Городу отправления
  - Городу назначения
  - Дате
- Просматривать детали интересующих поездок
- Видеть информацию о водителе

### 3. Заявки на поездки (Requests)

Система заявок обеспечивает безопасный процесс бронирования:

- **Отправка заявки** — пассажир подаёт заявку на конкретную поездку
- **Рассмотрение заявки** — водитель видит все заявки на свои поездки
- **Принятие/отклонение** — водитель решает принять или отклонить заявку
- **Статусы заявок:**
  - `PENDING` — ожидает рассмотрения
  - `APPROVED` — принята
  - `REJECTED` — отклонена
  - `CANCELLED` — отменена пассажиром

### 4. Управление профилем

- Просмотр информации о пользователе
- Редактирование профиля (имя, телефон, информация о себе)
- Просмотр истории поездок (в качестве водителя и пассажира)
- Рейтинг и отзывы

### 5. Система уведомлений

- Внутриприложенные уведомления
- Уведомления о:
  - Новых заявках на поездку
  - Изменении статуса заявки
  - Отмене поездки
  - Напоминании о предстоящей поездке
- Статусы прочитано/непрочитано

### 6. Система чатов

- Личные сообщения между пользователями
- Создание чатов для обсуждения деталей поездки
- Отправка и получение сообщений в реальном времени
- История переписки

### 7. Система отзывов и рейтинга

- Оценка пользователей после поездки
- Текстовые отзывы
- Рейтинг пользователей (1-5 звёзд)
- Отзывы от водителей и пассажиров друг о друге

---

## Архитектура системы

### Многоуровневая архитектура

Проект построен на принципах чистой архитектуры с чётким разделением на слои:

```
┌─────────────────────────────────────────────────────────┐
│                    API Layer                            │
│              (app/api — FastAPI Routers)               │
├─────────────────────────────────────────────────────────┤
│                 Service Layer                           │
│          (app/services — Business Logic)                │
├─────────────────────────────────────────────────────────┤
│              Repository Layer                           │
│       (app/repositories — Data Access)                 │
├─────────────────────────────────────────────────────────┤
│                 Domain Layer                            │
│           (app/domain — Enums, Models)                 │
├─────────────────────────────────────────────────────────┤
│                Database Models                         │
│          (app/models — SQLAlchemy Models)              │
└─────────────────────────────────────────────────────────┘
```

### API Layer (Слой API)

Обрабатывает HTTP запросы и возвращает ответы. Использует FastAPI для определения маршрутов и автоматической генерации документации.

**Компоненты:**

- [`app/api/auth.py`](backend/app/api/auth.py) — Эндпоинты аутентификации
- [`app/api/trips.py`](backend/app/api/trips.py) — Эндпоинты поездок
- [`app/api/requests.py`](backend/app/api/requests.py) — Эндпоинты заявок
- [`app/api/users.py`](backend/app/api/users.py) — Эндпоинты пользователей
- [`app/api/notifications.py`](backend/app/api/notifications.py) — Эндпоинты уведомлений
- [`app/api/chat.py`](backend/app/api/chat.py) — Эндпоинты чатов
- [`app/api/reviews.py`](backend/app/api/reviews.py) — Эндпоинты отзывов

### Service Layer (Слой сервисов)

Содержит бизнес-логику приложения. Каждый сервис отвечает за определённую область:

- [`app/services/auth_service.py`](backend/app/services/auth_service.py) — Логика аутентификации
- [`app/services/trip_service.py`](backend/app/services/trip_service.py) — Логика управления поездками
- [`app/services/request_service.py`](backend/app/services/request_service.py) — Логика обработки заявок
- [`app/services/chat_service.py`](backend/app/services/chat_service.py) — Логика чатов
- [`app/services/review_service.py`](backend/app/services/review_service.py) — Логика отзывов

### Repository Layer (Слой репозиториев)

Абстракция над источниками данных. Позволяет легко менять реализацию хранилища:

**Интерфейсы:**

- [`app/repositories/interfaces/user_repo.py`](backend/app/repositories/interfaces/user_repo.py)
- [`app/repositories/interfaces/trip_repo.py`](backend/app/repositories/interfaces/trip_repo.py)
- [`app/repositories/interfaces/request_repo.py`](backend/app/repositories/interfaces/request_repo.py)
- [`app/repositories/interfaces/notification_repo.py`](backend/app/repositories/interfaces/notification_repo.py)
- [`app/repositories/interfaces/refresh_token_repo.py`](backend/app/repositories/interfaces/refresh_token_repo.py)
- [`app/repositories/interfaces/chat_repo.py`](backend/app/repositories/interfaces/chat_repo.py)

**In-Memory реализации:**

- [`app/repositories/inmemory/user_repo.py`](backend/app/repositories/inmemory/user_repo.py)
- [`app/repositories/inmemory/trip_repo.py`](backend/app/repositories/inmemory/trip_repo.py)
- [`app/repositories/inmemory/request_repo.py`](backend/app/repositories/inmemory/request_repo.py)
- [`app/repositories/inmemory/notification_repo.py`](backend/app/repositories/inmemory/notification_repo.py)
- [`app/repositories/inmemory/refresh_token_repo.py`](backend/app/repositories/inmemory/refresh_token_repo.py)
- [`app/repositories/inmemory/chat_repo.py`](backend/app/repositories/inmemory/chat_repo.py)

**PostgreSQL реализации:**

- [`app/db/repositories/pg_user_repo.py`](backend/app/db/repositories/pg_user_repo.py)
- [`app/db/repositories/pg_trip_repo.py`](backend/app/db/repositories/pg_trip_repo.py)
- [`app/db/repositories/pg_request_repo.py`](backend/app/db/repositories/pg_request_repo.py)
- [`app/db/repositories/pg_notification_repo.py`](backend/app/db/repositories/pg_notification_repo.py)
- [`app/db/repositories/pg_refresh_token_repo.py`](backend/app/db/repositories/pg_refresh_token_repo.py)

### Domain Layer (Доменный слой)

Содержит доменные модели и перечисления:

- [`app/domain/enums.py`](backend/app/domain/enums.py) — Статусы поездок, заявок, типы уведомлений

### Database Models (Модели базы данных)

SQLAlchemy 2.0 модели для работы с PostgreSQL:

- [`app/db/models/user.py`](backend/app/db/models/user.py) — Модель пользователя
- [`app/db/models/trip.py`](backend/app/db/models/trip.py) — Модель поездки
- [`app/db/models/trip_request.py`](backend/app/db/models/trip_request.py) — Модель заявки
- [`app/db/models/notification.py`](backend/app/db/models/notification.py) — Модель уведомления
- [`app/db/models/refresh_token.py`](backend/app/db/models/refresh_token.py) — Модель refresh токена
- [`app/db/models/chat.py`](backend/app/db/models/chat.py) — Модель чата и сообщений
- [`app/db/models/review.py`](backend/app/db/models/review.py) — Модель отзыва

---

## Структура проекта

```
BlaBlaCar/
├── backend/                      # FastAPI приложение
│   ├── app/
│   │   ├── api/                  # API эндпоинты
│   │   │   ├── auth.py            # Аутентификация
│   │   │   ├── trips.py           # Поездки
│   │   │   ├── requests.py        # Заявки
│   │   │   ├── users.py           # Пользователи
│   │   │   ├── notifications.py   # Уведомления
│   │   │   ├── chat.py            # Чат и сообщения
│   │   │   ├── reviews.py         # Отзывы и рейтинг
│   │   │   ├── deps.py            # Зависимости для DI
│   │   │   └── __init__.py
│   │   ├── core/                  # Основная конфигурация
│   │   │   ├── config.py          # Настройки приложения
│   │   │   ├── security.py        # Безопасность (JWT, пароли)
│   │   │   ├── database.py        # Подключение к БД
│   │   │   ├── logger.py          # Логирование
│   │   │   ├── middleware.py      # Middleware (CORS, Request ID)
│   │   │   ├── exceptions.py      # Кастомные исключения
│   │   │   └── __init__.py
│   │   ├── db/                    # SQLAlchemy модели и репозитории
│   │   │   ├── models/            # ORM модели
│   │   │   │   ├── user.py
│   │   │   │   ├── trip.py
│   │   │   │   ├── trip_request.py
│   │   │   │   ├── notification.py
│   │   │   │   ├── refresh_token.py
│   │   │   │   ├── chat.py
│   │   │   │   ├── review.py
│   │   │   │   └── base.py
│   │   │   └── repositories/       # PostgreSQL репозитории
│   │   │       ├── pg_user_repo.py
│   │   │       ├── pg_trip_repo.py
│   │   │       ├── pg_request_repo.py
│   │   │       ├── pg_notification_repo.py
│   │   │       ├── pg_refresh_token_repo.py
│   │   │       ├── pg_chat_repo.py
│   │   │       └── pg_review_repo.py
│   │   ├── domain/                # Доменные модели
│   │   │   └── enums.py           # Перечисления (статусы)
│   │   ├── models/                # Pydantic модели
│   │   │   ├── user.py
│   │   │   ├── trip.py
│   │   │   ├── request.py
│   │   │   ├── notification.py
│   │   │   ├── chat.py
│   │   │   └── __init__.py
│   │   ├── repositories/          # Слой доступа к данным
│   │   │   ├── interfaces/        # Абстрактные интерфейсы
│   │   │   │   ├── user_repo.py
│   │   │   │   ├── trip_repo.py
│   │   │   │   ├── request_repo.py
│   │   │   │   ├── notification_repo.py
│   │   │   │   ├── refresh_token_repo.py
│   │   │   │   ├── chat_repo.py
│   │   │   │   ├── review_repo.py
│   │   │   │   └── __init__.py
│   │   │   ├── inmemory/          # In-memory реализации
│   │   │   │   ├── user_repo.py
│   │   │   │   ├── trip_repo.py
│   │   │   │   ├── request_repo.py
│   │   │   │   ├── notification_repo.py
│   │   │   │   ├── refresh_token_repo.py
│   │   │   │   ├── chat_repo.py
│   │   │   │   ├── review_repo.py
│   │   │   │   ├── locks.py        # Блокировки для конкурентности
│   │   │   │   └── __init__.py
│   │   │   └── __init__.py
│   │   ├── services/              # Бизнес-логика
│   │   │   ├── auth_service.py
│   │   │   ├── trip_service.py
│   │   │   ├── request_service.py
│   │   │   ├── chat_service.py
│   │   │   ├── review_service.py
│   │   │   └── __init__.py
│   │   ├── schemas/               # Pydantic схемы
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── trip.py
│   │   │   ├── request.py
│   │   │   ├── notification.py
│   │   │   ├── chat.py
│   │   │   ├── review.py
│   │   │   └── __init__.py
│   │   ├── background/            # Фоновые задачи
│   │   │   ├── worker.py          # Обработчик задач
│   │   │   ├── adapters.py        # Адаптеры для уведомлений
│   │   │   └── __init__.py
│   │   ├── utils/                 # Утилиты
│   │   │   └── mappers.py         # Мапперы данных
│   │   └── main.py                # Точка входа
│   ├── tests/                     # Тесты
│   │   ├── unit/                  # Модульные тесты
│   │   ├── integration/           # Интеграционные тесты
│   │   ├── concurrency/           # Тесты параллелизма
│   │   ├── conftest.py            # Pytest fixtures
│   │   └── test_*.py              # various test files
│   ├── requirements.txt            # Python зависимости
│   └── .env                       # Переменные окружения
│
├── frontend/                      # React приложение
│   ├── src/
│   │   ├── components/            # UI компоненты
│   │   │   ├── ui/               # Базовые UI компоненты
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Input.tsx
│   │   │   │   ├── Card.tsx
│   │   │   │   ├── Skeleton.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Layout.tsx        # Макет страницы
│   │   │   ├── Map.tsx           # Компонент карты
│   │   │   └── chat/             # Чат компоненты
│   │   │       ├── ChatList.tsx
│   │   │       ├── ChatWindow.tsx
│   │   │       └── MessageBubble.tsx
│   │   ├── pages/                # Страницы
│   │   │   ├── HomePage.tsx
│   │   │   ├── TripsPage.tsx
│   │   │   ├── TripPage.tsx
│   │   │   ├── CreateTripPage.tsx
│   │   │   ├── MyTripsPage.tsx
│   │   │   ├── LoginPage.tsx
│   │   │   ├── RegisterPage.tsx
│   │   │   ├── ProfilePage.tsx
│   │   │   ├── NotificationsPage.tsx
│   │   │   ├── MessagesPage.tsx
│   │   │   └── ChatPage.tsx
│   │   ├── services/             # API клиент
│   │   │   └── api.ts
│   │   ├── stores/               # Zustand стейт
│   │   │   └── auth.ts
│   │   ├── types/                # TypeScript типы
│   │   │   └── index.ts
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/
│   │   └── favicon.svg
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── index.html
│
├── plans/                        # Планы и документация
│   └── *.md
│
└── README.md                      # Документация
```

---

## Технологический стек

### Бэкенд

| Технология | Версия | Назначение |
|------------|--------|------------|
| FastAPI | latest | Веб-фреймворк |
| SQLAlchemy | 2.0 | ORM |
| PostgreSQL | latest | База данных (основная) |
| asyncpg | latest | Async драйвер для PostgreSQL |
| Pydantic | v2 | Валидация данных |
| Python-Jose | latest | JWT токены |
| Passlib | 1.7.4 | Хэширование паролей |
| Uvicorn | latest | ASGI сервер |
| Python | 3.10+ | Язык программирования |
| pytest | latest | Тестирование |
| pytest-asyncio | latest | Асинхронное тестирование |

### Фронтенд

| Технология | Версия | Назначение |
|------------|--------|------------|
| React | 18 | UI библиотека |
| TypeScript | 5 | Типизация |
| Vite | 5 | Сборщик |
| React Router | 6 | Маршрутизация |
| Axios | latest | HTTP клиент |
| Zustand | latest | Управление состоянием |

---

## Модели данных

### User (Пользователь)

```python
class User:
    id: str              # UUID
    email: str           # Email (уникальный)
    password_hash: str  # Хэш пароля
    name: str            # Имя
    phone: str           # Телефон (опционально)
    avatar_url: str      # URL аватара (опционально)
    rating: float        # Средний рейтинг
    created_at: datetime # Дата создания
    updated_at: datetime # Дата обновления
```

### Trip (Поездка)

```python
class Trip:
    id: str              # UUID
    driver_id: str       # ID водителя
    origin: str          # Город отправления
    destination: str     # Город назначения
    departure_time: datetime  # Время отправления
    available_seats: int # Доступные места
    price: float         # Цена за место
    status: TripStatus   # Статус поездки
    description: str    # Описание (опционально)
    created_at: datetime # Дата создания
    updated_at: datetime # Дата обновления
```

**Статусы поездки (TripStatus):**

- `ACTIVE` — Активна (доступна для бронирования)
- `COMPLETED` — Завершена
- `CANCELLED` — Отменена

### Request (Заявка)

```python
class Request:
    id: str              # UUID
    trip_id: str         # ID поездки
    passenger_id: str    # ID пассажира
    seats_requested: int # Запрошено мест
    message: str         # Сообщение (опционально)
    status: RequestStatus # Статус заявки
    created_at: datetime # Дата создания
    updated_at: datetime # Дата обновления
```

**Статусы заявки (RequestStatus):**

- `PENDING` — Ожидает рассмотрения
- `APPROVED` — Принята
- `REJECTED` — Отклонена
- `CANCELLED` — Отменена пассажиром

### Notification (Уведомление)

```python
class Notification:
    id: str              # UUID
    user_id: str         # ID получателя
    type: NotificationType # Тип уведомления
    title: str           # Заголовок
    message: str         # Сообщение
    is_read: bool        # Прочитано/непрочитано
    related_trip_id: str # ID связанной поездки (опционально)
    related_request_id: str # ID связанной заявки (опционально)
    created_at: datetime # Дата создания
```

**Типы уведомлений (NotificationType):**

- `NEW_REQUEST` — Новая заявка
- `REQUEST_APPROVED` — Заявка принята
- `REQUEST_REJECTED` — Заявка отклонена
- `TRIP_CANCELLED` — Поездка отменена
- `REQUEST_CANCELLED` — Заявка отменена
- `NEW_MESSAGE` — Новое сообщение
- `NEW_REVIEW` — Новый отзыв

### Chat (Чат)

```python
class Chat:
    id: str              # UUID
    trip_id: str         # ID связанной поездки (опционально)
    participants: list   # Участники чата
    created_at: datetime # Дата создания
    updated_at: datetime # Дата обновления

class Message:
    id: str              # UUID
    chat_id: str         # ID чата
    sender_id: str       # ID отправителя
    content: str         # Текст сообщения
    created_at: datetime # Дата отправки
    is_read: bool        # Прочитано/непрочитано
```

### Review (Отзыв)

```python
class Review:
    id: str              # UUID
    author_id: str       # ID автора отзыва
    target_id: str       # ID пользователя, о котором отзыв
    trip_id: str         # ID поездки
    rating: int          # Оценка (1-5)
    comment: str         # Текст отзыва (опционально)
    review_type: ReviewType # Тип отзыва (driver_to_passenger, passenger_to_driver)
    created_at: datetime # Дата создания
```

---

## API эндпоинты

### Аутентификация

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/auth/register` | Регистрация нового пользователя | Нет |
| POST | `/api/auth/login` | Вход в систему | Нет |
| GET | `/api/auth/me` | Получение текущего пользователя | Да |
| POST | `/api/auth/refresh` | Обновление токена | Да |
| POST | `/api/auth/logout` | Выход из системы | Да |

### Поездки

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/trips` | Создание поездки | Да |
| GET | `/api/trips` | Поиск поездок | Да |
| GET | `/api/trips/{id}` | Получение поездки по ID | Да |
| PUT | `/api/trips/{id}` | Обновление поездки | Да (только водитель) |
| DELETE | `/api/trips/{id}` | Удаление поездки | Да (только водитель) |
| GET | `/api/trips/my/driver` | Мои поездки как водитель | Да |

### Заявки

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/trips/{id}/requests` | Создание заявки | Да |
| GET | `/api/requests/my` | Мои заявки как пассажир | Да |
| GET | `/api/trips/{id}/requests` | Получение заявок поездки | Да (только водитель) |
| PUT | `/api/requests/{id}` | Обновление статуса заявки | Да |

### Пользователи

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| GET | `/api/users/{id}` | Получение профиля | Да |
| PUT | `/api/users/{id}` | Обновление профиля | Да |
| GET | `/api/users/{id}/trips` | Получение поездок пользователя | Да |
| GET | `/api/users/{id}/reviews` | Получение отзывов о пользователе | Да |

### Уведомления

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| GET | `/api/notifications` | Получение уведомлений | Да |
| PUT | `/api/notifications/{id}/read` | Отметить как прочитанное | Да |
| PUT | `/api/notifications/read-all` | Прочитать все | Да |

### Чат

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| GET | `/api/chats` | Получение списка чатов | Да |
| POST | `/api/chats` | Создание чата | Да |
| GET | `/api/chats/{id}` | Получение чата с сообщениями | Да |
| POST | `/api/chats/{id}/messages` | Отправка сообщения | Да |

### Отзывы

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/reviews` | Создание отзыва | Да |
| GET | `/api/users/{id}/reviews` | Получение отзывов о пользователе | Да |

---

## Бизнес-логика

### AuthService

Сервис аутентификации отвечает за:

- Регистрацию новых пользователей с валидацией email
- Создание JWT токенов при успешном входе
- Проверку паролей
- Генерацию и валидацию refresh токенов
- Получение информации о текущем пользователе

### TripService

Сервис поездок управляет жизненным циклом поездок:

- Создание поездок с валидацией данных
- Поиск поездок по критериям (город, дата)
- Обновление информации о поездке
- Отмена поездок (только водителем)
- Завершение поездок (только водителем)
- Проверка доступности мест

### RequestService

Сервис заявок управляет процессом бронирования:

- Создание заявок на поездку
- Проверка доступности мест перед созданием заявки
- Принятие заявок (уменьшение доступных мест)
- Отклонение заявок
- Отмена заявок пассажиром
- Обработка параллельных заявок с использованием блокировок

### ChatService

Сервис чатов обеспечивает коммуникацию между пользователями:

- Создание чатов (личных или связанных с поездкой)
- Отправка и получение сообщений
- Получение истории переписки
- Проверка участников чата

### ReviewService

Сервис отзывов управляет системой рейтинга:

- Создание отзывов после поездки
- Расчёт среднего рейтинга пользователя
- Проверка, что поездка была завершена
- Получение отзывов о пользователе

---

## Система уведомлений

Система уведомлений информирует пользователей о важных событиях:

- **Внутриприложенные уведомления** — не требуют email или push-уведомлений
- **Автоматическая генерация** — уведомления создаются сервисами при наступлении событий
- **Статусы прочитано/непрочитано** — пользователь может отмечать уведомления
- **Связанные объекты** — уведомления содержат ссылки на связанные поездки и заявки

### Типы уведомлений

| Тип | Описание | Когда создаётся |
|-----|----------|----------------|
| NEW_REQUEST | Новая заявка | Пассажир подаёт заявку на поездку |
| REQUEST_APPROVED | Заявка принята | Водитель принимает заявку |
| REQUEST_REJECTED | Заявка отклонена | Водитель отклоняет заявку |
| TRIP_CANCELLED | Поездка отменена | Водитель отменяет поездку |
| REQUEST_CANCELLED | Заявка отменена | Пассажир отменяет свою заявку |
| NEW_MESSAGE | Новое сообщение | Пользователь получает сообщение |
| NEW_REVIEW | Новый отзыв | Пользователь получает отзыв |

---

## Система чатов

Система чатов позволяет пользователям общаться между собой:

- **Личные чаты** — для общения между двумя пользователями
- **Чаты поездок** — привязанные к конкретной поездке
- **История сообщений** — все сообщения сохраняются
- **Индикация прочтения** — видно, прочитано ли сообщение

### Использование

1. Пользователь может начать чат с другим пользователем
2. Чат можно привязать к поездке для контекста
3. Сообщения отправляются мгновенно
4. История доступна в любое время

---

## Система отзывов

Система рейтинга и отзывов повышает доверие между пользователями:

- **Оценка 1-5 звёзд** — количественная оценка
- **Текстовый комментарий** — качественный отзыв
- **Типы отзывов:**
  - От водителя пассажиру
  - От пассажира водителю
- **Средний рейтинг** — автоматически рассчитывается для каждого пользователя

### Правила

- Оставить отзыв можно только о завершённой поездке
- Один отзыв на пользователя за поездку
- Автор отзыва видит только свои отзывы

---

## Безопасность

### Аутентификация

- **JWT токены** — используются для защиты API endpoints
- **Access tokens** — краткосрочные токены (24 часа по умолчанию)
- **Refresh tokens** — долгосрочные токены для обновления access токена

### Хэширование паролей

- **bcrypt** — используется для безопасного хэширования паролей
- **Соль** — автоматически генерируется для каждого пароля

### Защищённые маршруты

- Большинство API endpoints требуют аутентификации
- Токен передаётся в заголовке `Authorization: Bearer <token>`

### CORS

- Настроена политика CORS для разрешённых источников
- По умолчанию разрешены localhost:5173 и localhost:3000

---

## Тестирование

Проект включает комплексные тесты:

### Типы тестов

- **Модульные тесты** — тестирование отдельных компонентов в изоляции
- **Интеграционные тесты** — тестирование взаимодействия компонентов
- **Тесты параллелизма** — тестирование потокобезопасных операций

### Запуск тестов

```bash
pytest
```

### Покрытие

Тесты покрывают основные сценарии:
- Регистрация и вход пользователей
- Создание и поиск поездок
- Заявки и их обработка
- Параллельные заявки на одно место

---

## Конкурентность и блокировки

Система использует механизм блокировок для обработки параллельных заявок:

### Проблема

При одновременной подаче заявок несколькими пассажирами на последнее место в поездке может возникнуть race condition.

### Решение

- **Блокировка на уровне поездки** — используется `asyncio.Lock` для каждой поездки
- **Атомарные операции** — проверка и бронирование места происходят в одном блоке
- **Очередь обработки** — заявки обрабатываются последовательно

### Реализация

```python
# В request_service.py
async def create_request(trip_id: str, passenger_id: str, ...):
    async with trip_locks[trip_id]:
        # Проверка доступности мест
        # Создание заявки
        # Обновление количества мест
```

---

## Конфигурация

### Переменные окружения

Создайте файл `.env` в директории `backend/`:

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
# PostgreSQL настройки (если USE_POSTGRESQL=True)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DB=blablacar
```

### Переключение хранилища

- `USE_POSTGRESQL=False` — используется in-memory хранилище (для разработки)
- `USE_POSTGRESQL=True` — используется PostgreSQL (для продакшена)

---

## Запуск и разработка

### Требования

- Python 3.10+
- Node.js 18+
- npm

### Установка и запуск

#### Бэкенд

```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/MacOS: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Фронтенд

```bash
cd frontend
npm install
npm run dev
```

### Доступ к приложению

- **Бэкенд API:** http://localhost:8000
- **API документация:** http://localhost:8000/docs
- **Фронтенд:** http://localhost:5173
