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
10. [Безопасность](#безопасность)
11. [Тестирование](#тестирование)
12. [Конкурентность и блокировки](#конкурентность-и-блокировки)
13. [Конфигурация](#конфигурация)
14. [Запуск и разработка](#запуск-и-разработка)

---

## Введение

**RoadMate** — это полноценное веб-приложение для поиска и организации совместных поездок (карпулинга), аналог популярного сервиса BlaBlaCar. Проект разработан с использованием современных технологий и следует принципам чистой архитектуры.

### Назначение проекта

Платформа позволяет водителям создавать поездки из одного города в другой, а пассажирам — находить и бронировать места в этих поездках. Это обеспечивает удобный и экономически выгодный способ перемещения между городами.

### Ключевые характеристики

- **Полный цикл:** от поиска поездки до завершения поездки
- **Асинхронная обработка:** использование FastAPI и фоновых воркеров
- **База данных:** PostgreSQL с async драйвером (sqlalchemy + asyncpg)
- **Безопасность:** JWT аутентификация, хэширование паролей
- **Масштабируемость:** паттерн репозитория для абстракции данных
- **Тестируемость:** комплексное покрытие тестами

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
- Рейтинг и отзывы (планируется)

### 5. Система уведомлений

- Внутриприложенные уведомления
- Уведомления о:
  - Новых заявках на поездку
  - Изменении статуса заявки
  - Отмене поездки
  - Напоминании о предстоящей поездке
- Статусы прочитано/непрочитано

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
│           (app/domain — Enums, Models)                  │
├─────────────────────────────────────────────────────────┤
│                Database Models                         │
│          (app/models — SQLAlchemy Models)               │
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

### Service Layer (Слой сервисов)

Содержит бизнес-логику приложения. Каждый сервис отвечает за определённую область:

- [`app/services/auth_service.py`](backend/app/services/auth_service.py) — Логика аутентификации
- [`app/services/trip_service.py`](backend/app/services/trip_service.py) — Логика управления поездками
- [`app/services/request_service.py`](backend/app/services/request_service.py) — Логика обработки заявок

### Repository Layer (Слой репозиториев)

Абстракция над источниками данных. Позволяет легко менять реализацию хранилища:

**Интерфейсы:**

- [`app/repositories/interfaces/user_repo.py`](backend/app/repositories/interfaces/user_repo.py)
- [`app/repositories/interfaces/trip_repo.py`](backend/app/repositories/interfaces/trip_repo.py)
- [`app/repositories/interfaces/request_repo.py`](backend/app/repositories/interfaces/request_repo.py)
- [`app/repositories/interfaces/notification_repo.py`](backend/app/repositories/interfaces/notification_repo.py)
- [`app/repositories/interfaces/refresh_token_repo.py`](backend/app/repositories/interfaces/refresh_token_repo.py)

**In-Memory реализации:**

- [`app/repositories/inmemory/user_repo.py`](backend/app/repositories/inmemory/user_repo.py)
- [`app/repositories/inmemory/trip_repo.py`](backend/app/repositories/inmemory/trip_repo.py)
- [`app/repositories/inmemory/request_repo.py`](backend/app/repositories/inmemory/request_repo.py)
- [`app/repositories/inmemory/notification_repo.py`](backend/app/repositories/inmemory/notification_repo.py)
- [`app/repositories/inmemory/refresh_token_repo.py`](backend/app/repositories/inmemory/refresh_token_repo.py)

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
│   │   │   ├── deps.py            # Зависимости для DI
│   │   │   └── __init__.py
│   │   ├── core/                  # Основная конфигурация
│   │   │   ├── config.py          # Настройки приложения
│   │   │   ├── security.py        # Безопасность (JWT, пароли)
│   │   │   ├── database.py        # Подключение к БД (PostgreSQL + in-memory)
│   │   │   ├── logger.py          # Логирование
│   │   │   ├── middleware.py      # Middleware (CORS, Request ID)
│   │   │   ├── exceptions.py      # Кастомные исключения
│   │   │   └── __init__.py
│   │   │   ├── db/                 # SQLAlchemy модели и репозитории
│   │   │   │   ├── models/        # ORM модели
│   │   │   │   │   ├── user.py
│   │   │   │   │   ├── trip.py
│   │   │   │   │   ├── trip_request.py
│   │   │   │   │   ├── notification.py
│   │   │   │   │   ├── refresh_token.py
│   │   │   │   │   └── base.py
│   │   │   │   └── repositories/   # PostgreSQL репозитории
│   │   │   │       ├── pg_user_repo.py
│   │   │   │       ├── pg_trip_repo.py
│   │   │   │       ├── pg_request_repo.py
│   │   │   │       ├── pg_notification_repo.py
│   │   │   │       └── pg_refresh_token_repo.py
│   │   ├── domain/                # Доменные модели
│   │   │   └── enums.py           # Перечисления (статусы)
│   │   ├── models/                # SQLAlchemy модели
│   │   │   ├── user.py
│   │   │   ├── trip.py
│   │   │   ├── request.py
│   │   │   ├── notification.py
│   │   │   └── __init__.py
│   │   ├── repositories/          # Слой доступа к данным
│   │   │   ├── interfaces/        # Абстрактные интерфейсы
│   │   │   │   ├── user_repo.py
│   │   │   │   ├── trip_repo.py
│   │   │   │   ├── request_repo.py
│   │   │   │   ├── notification_repo.py
│   │   │   │   ├── refresh_token_repo.py
│   │   │   │   └── __init__.py
│   │   │   ├── inmemory/          # In-memory реализации
│   │   │   │   ├── user_repo.py
│   │   │   │   ├── trip_repo.py
│   │   │   │   ├── request_repo.py
│   │   │   │   ├── notification_repo.py
│   │   │   │   ├── refresh_token_repo.py
│   │   │   │   ├── locks.py        # Блокировки для конкурентности
│   │   │   │   └── __init__.py
│   │   │   ├── user_repo.py
│   │   │   ├── trip_repo.py
│   │   │   ├── request_repo.py
│   │   │   ├── notification_repo.py
│   │   │   └── __init__.py
│   │   ├── services/              # Бизнес-логика
│   │   │   ├── auth_service.py
│   │   │   ├── trip_service.py
│   │   │   ├── request_service.py
│   │   │   └── __init__.py
│   │   ├── schemas/               # Pydantic схемы
│   │   │   ├── auth.py
│   │   │   ├── user.py
│   │   │   ├── trip.py
│   │   │   ├── request.py
│   │   │   ├── notification.py
│   │   │   └── __init__.py
│   │   ├── background/            # Фоновые задачи
│   │   │   ├── worker.py          # Обработчик задач
│   │   │   ├── adapters.py        # Адаптеры для уведомлений
│   │   │   └── __init__.py
│   │   └── main.py                # Точка входа
│   ├── tests/                     # Тесты
│   │   ├── unit/                  # Модульные тесты
│   │   ├── integration/           # Интеграционные тесты
│   │   ├── concurrency/           # Тесты параллелизма
│   │   ├── conftest.py            # Pytest fixtures
│   │   ├── test_*.py              # various test files
│   ├── requirements.txt          # Python зависимости
│   └── .env                       # Переменные окружения
│
├── frontend/                      # React приложение
│   ├── src/
│   │   ├── components/            # UI компоненты
│   │   ├── pages/                 # Страницы
│   │   ├── services/              # API клиент
│   │   ├── stores/                # Zustand стейт
│   │   ├── types/                 # TypeScript типы
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
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
| Alembic | latest | Миграции БД |

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
    created_at: datetime # Дата создания
```

**Типы уведомлений (NotificationType):**

- `NEW_REQUEST` — Новая заявка
- `REQUEST_APPROVED` — Заявка принята
- `REQUEST_REJECTED` — Заявка отклонена
- `TRIP_CANCELLED` — Поездка отменена
- `REQUEST_CANCELLED` — Заявка отменена

---

## API эндпоинты

### Аутентификация

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/auth/register` | Регистрация нового пользователя | Нет |
| POST | `/api/auth/login` | Вход в систему | Нет |
| GET | `/api/auth/me` | Получение текущего пользователя | Да |
| POST | `/api/auth/refresh` | Обновление токена | Да |

### Поездки

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/trips` | Создание поездки | Да |
| GET | `/api/trips` | Поиск поездок | Да |
| GET | `/api/trips/{id}` | Получение поездки по ID | Да |
| PUT | `/api/trips/{id}` | Обновление поездки | Да (только водитель) |
| DELETE | `/api/trips/{id}` | Удаление поездки | Да (только водитель) |

### Заявки

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| POST | `/api/trips/{id}/request` | Создание заявки | Да |
| GET | `/api/requests` | Получение заявок пользователя | Да |
| GET | `/api/trips/{id}/requests` | Получение заявок поездки | Да (только водитель) |
| PUT | `/api/requests/{id}` | Обновление статуса заявки | Да |

### Пользователи

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| GET | `/api/users/{id}` | Получение профиля | Да |
| PUT | `/api/users/{id}` | Обновление профиля | Да |
| GET | `/api/users/{id}/trips` | Получение поездок пользователя | Да |

### Уведомления

| Метод | Эндпоинт | Описание | Авторизация |
|-------|----------|----------|-------------|
| GET | `/api/notifications` | Получение уведомлений | Да |
| PUT | `/api/notifications/{id}/read` | Отметить как прочитанное | Да |
| PUT | `/api/notifications/read-all` | Прочитать все | Да |

---

## Бизнес-логика

### AuthService

Сервис аутентификации отвечает за:

- Регистрацию новых пользователей с валидацией email
- Создание JWT токенов при успешном входе
- Проверку паролей
- Генерацию и валидацию refresh токенов
- Получение информации о текущем пользователе

**Основные методы:**

- `register(email, password, name)` — Регистрация
- `login(email, password)` — Вход
- `refresh_access_token(refresh_token)` — Обновление токена
- `get_current_user(token)` — Получение текущего пользователя

### TripService

Сервис поездок управляет жизненным циклом поездок:

- Создание поездок с валидацией данных
- Поиск поездок по критериям (город, дата)
- Обновление информации о поездке
- Отмена поездок (только водителем)
- Завершение поездок (только водителем)
- Проверка доступности мест

**Основные методы:**

- `create_trip(driver_id, trip_data)` — Создание поездки
- `search_trips(origin, destination, date)` — Поиск поездок
- `get_trip(trip_id)` — Получение поездки
- `update_trip(trip_id, driver_id, data)` — Обновление
- `cancel_trip(trip_id, driver_id)` — Отмена
- `complete_trip(trip_id, driver_id)` — Завершение

### RequestService

Сервис заявок обрабатывает взаимодействие между пассажирами и водителями:

- Создание заявок на поездку
- Валидация доступности мест (конкурентная)
- Принятие заявок водителем
- Отклонение заявок водителем
- Отмена заявок пассажиром
- Обработка конкурентных заявок

**Основные методы:**

- `create_request(passenger_id, trip_id)` — Создание заявки
- `approve_request(request_id, driver_id)` — Принятие заявки
- `reject_request(request_id, driver_id)` — Отклонение заявки
- `cancel_request(request_id, passenger_id)` — Отмена заявки
- `get_trip_requests(trip_id, driver_id)` — Получение заявок поездки
- `get_passenger_requests(passenger_id)` — Получение заявок пассажира

**Конкурентность:**

Сервис использует блокировки для обеспечения корректной обработки нескольких заявок одновременно. Это предотвращает ситуации, когда количество принятых заявок превышает доступные места.

---

## Система уведомлений

### Архитектура

Система уведомлений состоит из нескольких компонентов:

1. **Модель уведомления** — хранение данных в БД
2. **Репозиторий уведомлений** — доступ к данным
3. **Background Worker** — асинхронная отправка
4. **Адаптеры** — различные каналы доставки

### Типы событий

Уведомления генерируются при следующих событиях:

| Событие | Получатель | Тип уведомления |
|---------|------------|-----------------|
| Новая заявка на поездку | Водитель | NEW_REQUEST |
| Заявка принята | Пассажир | REQUEST_APPROVED |
| Заявка отклонена | Пассажир | REQUEST_REJECTED |
| Поездка отменена | Пассажиры (принятые заявки) | TRIP_CANCELLED |
| Заявка отменена | Водитель | REQUEST_CANCELLED |

### Workflow

```
Действие пользователя
        │
        ▼
API Endpoint вызывает Service
        │
        ▼
Service выполняет бизнес-логику
        │
        ▼
Service создает уведомление в БД
        │
        ▼
Background Worker обрабатывает очередь
        │
        ▼
Адаптеры отправляют уведомление
```

---

## Безопасность

### Аутентификация

- **JWT токены** — краткосрочные токены доступа (по умолчанию 24 часа)
- **Refresh токены** — долгосрочные токены для обновления доступа
- **Хэширование паролей** — использование bcrypt с солью
- **Валидация email** — проверка формата email

### Авторизация

- Защищённые маршруты требуют валидный JWT токен
- Проверка прав доступа к ресурсам (например, только водитель может редактировать свою поездку)
- Использование dependency injection для внедрения текущего пользователя

### Защита данных

- CORS настроен для разрешённых источников
- Rate limiting (при необходимости)
- Логирование запросов с request_id для трассировки
- Обработка исключений с безопасными сообщениями об ошибках

---

## Тестирование

### Типы тестов

Проект включает комплексное покрытие тестами:

#### Модульные тесты (Unit Tests)

Тестирование отдельных компонентов в изоляции:

- [`tests/unit/test_auth_service.py`](backend/tests/unit/test_auth_service.py) — Тесты сервиса аутентификации
- [`tests/unit/test_trip_service.py`](backend/tests/unit/test_trip_service.py) — Тесты сервиса поездок

#### Интеграционные тесты

Тестирование взаимодействия между компонентами:

- [`tests/integration/test_full_flow.py`](backend/tests/integration/test_full_flow.py) — Полный сценарий использования

#### Тесты параллелизма

Тестирование корректности при одновременных запросах:

- [`tests/concurrency/test_request_concurrency.py`](backend/tests/concurrency/test_request_concurrency.py)
- [`tests/test_request_service_concurrency.py`](backend/tests/test_request_service_concurrency.py)

#### Другие тесты

- [`tests/test_auth_service.py`](backend/tests/test_auth_service.py)
- [`tests/test_repositories.py`](backend/tests/test_repositories.py)
- [`tests/test_mappers.py`](backend/tests/test_mappers.py)
- [`tests/test_notification_pipeline.py`](backend/tests/test_notification_pipeline.py)
- [`tests/test_exception_handlers.py`](backend/tests/test_exception_handlers.py)
- [`tests/test_status_transitions.py`](backend/tests/test_status_transitions.py)

### Запуск тестов

```bash
# Запуск всех тестов
pytest

# Запуск с покрытием
pytest --cov=app

# Запуск конкретного файла
pytest tests/test_auth_service.py

# Запуск с детальным выводом
pytest -v
```

### Fixtures

В [`tests/conftest.py`](backend/tests/conftest.py) определены основные fixtures:

- `test_app` — приложение FastAPI для тестирования
- `test_client` — HTTP клиент для тестирования
- `test_db` — тестовая база данных
- `test_user` — тестовый пользователь
- `test_trip` — тестовая поездка

---

## Конкурентность и блокировки

### Проблема

При одновременной подаче нескольких заявок на поездку с ограниченным количеством мест может возникнуть ситуация гонки (race condition), когда несколько заявок будут приняты, превысив доступное количество мест.

### Решение

Используется механизм блокировок на уровне поездки:

1. При попытке создать заявку запрашивается блокировка на поездку
2. Проверяется количество принятых заявок
3. Если места доступны — заявка создаётся
4. Блокировка освобождается

### Реализация

В [`app/repositories/inmemory/locks.py`](backend/app/repositories/inmemory/locks.py) реализована система блокировок:

```python
class TripLocks:
    def acquire(self, trip_id: str) -> bool:
        """Получить блокировку для поездки"""
        
    def release(self, trip_id: str) -> None:
        """Освободить блокировку"""
        
    async def __aenter__(self):
        """Контекстный менеджер"""
        
    async def __aexit__(self):
        """Выход из контекста"""
```

### Тесты конкурентности

Тесты в [`tests/test_request_service_concurrency.py`](backend/tests/test_request_service_concurrency.py) проверяют:

- Одновременную подачу заявок несколькими пассажирами
- Корректное количество принятых заявок
- Отклонение лишних заявок при нехватке мест

---

## Конфигурация

### Переменные окружения

Файл `.env` в директории `backend/`:

```env
# Приложение
APP_NAME=Ride Sharing API
DEBUG=True

# JWT
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
ALLOWED_ORIGINS=["http://localhost:5173","http://localhost:3000"]

# База данных (PostgreSQL)
USE_POSTGRESQL=True
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/roadmate_db
```

### Конфигурация в коде

Вся конфигурация сосредоточена в [`app/core/config.py`](backend/app/core/config.py):

```python
class Settings(BaseSettings):
    app_name: str = "Ride Sharing API"
    debug: bool = False
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 1440
    
    # CORS
    allowed_origins: list[str]
    
    # Database
    use_postgresql: bool = False
    database_url: str = "sqlite:///./app.db"
```

### Архитектура базы данных

Проект поддерживает два режима работы с данными:

1. **In-Memory Storage** — для разработки и тестирования (по умолчанию)
2. **PostgreSQL** — для production использования

#### PostgreSQL конфигурация

При включенном `USE_POSTGRESQL=True`:

- Используется async драйвер `asyncpg` для высокой производительности
- SQLAlchemy 2.0 с async support
- Автоматическое создание таблиц при старте приложения
- Connection pooling для эффективной работы

#### Репозитории

Для PostgreSQL реализованы соответствующие репозитории:

- [`app/db/repositories/pg_user_repo.py`](backend/app/db/repositories/pg_user_repo.py)
- [`app/db/repositories/pg_trip_repo.py`](backend/app/db/repositories/pg_trip_repo.py)
- [`app/db/repositories/pg_request_repo.py`](backend/app/db/repositories/pg_request_repo.py)
- [`app/db/repositories/pg_notification_repo.py`](backend/app/db/repositories/pg_notification_repo.py)
- [`app/db/repositories/pg_refresh_token_repo.py`](backend/app/db/repositories/pg_refresh_token_repo.py)

Все репозитории реализуют интерфейсы из [`app/repositories/interfaces/`](backend/app/repositories/interfaces/), что обеспечивает единообразный API независимо от типа хранилища.

---

## Запуск и разработка

### Требования

- Python 3.10+
- Node.js 18+
- npm

### Установка и запуск бэкенда

```bash
# Переход в директорию бэкенда
cd backend

# Создание виртуального окружения
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/MacOS)
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Запуск сервера
uvicorn app.main:app --reload --port 8000
```

### Установка и запуск фронтенда

```bash
# Переход в директорию фронтенда
cd frontend

# Установка зависимостей
npm install

# Запуск dev сервера
npm run dev
```

### Доступ к приложению

- Бэкенд: http://localhost:8000
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Фронтенд: http://localhost:5173 (или http://localhost:5174)

---

## Планы развития

Проект находится в активной разработке. Возможные направления:

- [x] ~~Добавление PostgreSQL в качестве базы данных~~ (РЕАЛИЗОВАНО)
- Реализация real-time уведомлений через WebSockets
- Добавление рейтингов и отзывов
- Интеграция с платёжными системами
- Мобильное приложение
- Docker контейнеризация
- CI/CD пайплайны
