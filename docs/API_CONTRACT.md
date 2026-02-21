# API Contract — Приложение для поиска попутчиков

> Версия: 1.0 (MVP)
> Base URL: `http://localhost:8000/api`

## Содержание

1. [Общие соглашения](#общие-соглашения)
2. [Аутентификация](#auth---аутентификация)
3. [Поездки](#trips---поездки)
4. [Заявки](#requests---заявки)
5. [Пользователи](#users---пользователи)
6. [Уведомления](#notifications---уведомления)
7. [Коды ошибок](#коды-ошибок)

---

## Общие соглашения

### Формат запросов

- **Content-Type**: `application/json`
- **Кодировка**: UTF-8

### Аутентификация

Все защищённые endpoints требуют JWT токен в заголовке:

```
Authorization: Bearer <access_token>
```

### Пагинация

Список endpoints возвращают пагинированный ответ:

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "pages": 5
}
```

### timestamps

Все даты в формате ISO 8601:
- Дата: `YYYY-MM-DD`
- Время: `HH:MM:SS` (24-часовой формат)
- Дата и время: `YYYY-MM-DDTHH:MM:SSZ` (UTC)

---

## AUTH — Аутентификация

### Регистрация пользователя

**Endpoint:** `POST /auth/register`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123",
  "name": "Иван",
  "phone": "+79001234567"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Иван",
  "phone": "+79001234567",
  "avatar_url": null,
  "rating": null,
  "created_at": "2024-03-01T10:00:00Z"
}
```

**Errors:**
- `400` — Email уже зарегистрирован
- `422` — Ошибка валидации

---

### Вход пользователя

**Endpoint:** `POST /auth/login`

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securePassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "name": "Иван",
    "phone": "+79001234567",
    "avatar_url": null,
    "rating": null
  }
}
```

**Errors:**
- `401` — Неверный email или пароль

---

### Текущий пользователь

**Endpoint:** `GET /auth/me`

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Иван",
  "phone": "+79001234567",
  "avatar_url": "https://...",
  "rating": 4.8,
  "created_at": "2024-03-01T10:00:00Z"
}
```

**Errors:**
- `401` — Токен недействителен или истёк

---

## TRIPS — Поездки

### Создание поездки

**Endpoint:** `POST /trips`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "from_city": "Москва",
  "to_city": "Санкт-Петербург",
  "departure_date": "2024-03-15",
  "departure_time": "10:00",
  "available_seats": 3,
  "price_per_seat": 1500,
  "description": "Комфортная поездка, остановки по желанию"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "driver_id": "uuid",
  "driver": {
    "id": "uuid",
    "name": "Иван",
    "avatar_url": null,
    "rating": 4.8
  },
  "from_city": "Москва",
  "to_city": "Санкт-Петербург",
  "departure_date": "2024-03-15",
  "departure_time": "10:00",
  "available_seats": 3,
  "price_per_seat": 1500,
  "description": "Комфортная поездка, остановки по желанию",
  "status": "active",
  "created_at": "2024-03-01T10:00:00Z"
}
```

**Errors:**
- `401` — Не авторизован
- `422` — Ошибка валидации

---

### Поиск поездок

**Endpoint:** `GET /trips`

**Query Parameters:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `from_city` | string | Да | Город отправления |
| `to_city` | string | Да | Город прибытия |
| `date` | string | Нет | Дата поездки (YYYY-MM-DD) |
| `page` | integer | Нет | Номер страницы (по умолчанию: 1) |
| `page_size` | integer | Нет | Размер страницы (по умолчанию: 20) |

**Example:**
```
GET /trips?from_city=Москва&to_city=Санкт-Петербург&date=2024-03-15
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "uuid",
      "driver_id": "uuid",
      "driver": {
        "id": "uuid",
        "name": "Иван",
        "avatar_url": null,
        "rating": 4.8
      },
      "from_city": "Москва",
      "to_city": "Санкт-Петербург",
      "departure_date": "2024-03-15",
      "departure_time": "10:00",
      "available_seats": 3,
      "price_per_seat": 1500,
      "status": "active"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

### Получить поездку по ID

**Endpoint:** `GET /trips/{trip_id}`

**Response (200 OK):**
```json
{
  "id": "uuid",
  "driver_id": "uuid",
  "driver": {
    "id": "uuid",
    "name": "Иван",
    "phone": "+79001234567",
    "avatar_url": "https://...",
    "rating": 4.8,
    "created_at": "2024-01-01T10:00:00Z"
  },
  "from_city": "Москва",
  "to_city": "Санкт-Петербург",
  "departure_date": "2024-03-15",
  "departure_time": "10:00",
  "available_seats": 3,
  "price_per_seat": 1500,
  "description": "Комфортная поездка, остановки по желанию",
  "status": "active",
  "created_at": "2024-03-01T10:00:00Z"
}
```

**Errors:**
- `404` — Поездка не найдена

---

### Обновить поездку

**Endpoint:** `PUT /trips/{trip_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "from_city": "Москва",
  "to_city": "Санкт-Петербург",
  "departure_date": "2024-03-15",
  "departure_time": "11:00",
  "available_seats": 2,
  "price_per_seat": 1400,
  "description": "Обновлённое описание"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "driver_id": "uuid",
  "from_city": "Москва",
  "to_city": "Санкт-Петербург",
  "departure_date": "2024-03-15",
  "departure_time": "11:00",
  "available_seats": 2,
  "price_per_seat": 1400,
  "description": "Обновлённое описание",
  "status": "active",
  "created_at": "2024-03-01T10:00:00Z"
}
```

**Errors:**
- `401` — Не авторизован
- `403` — Не владелец поездки
- `404` — Поездка не найдена

---

### Удалить поездку

**Endpoint:** `DELETE /trips/{trip_id}`

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

**Errors:**
- `401` — Не авторизован
- `403` — Не владелец поездки
- `404` — Поездка не найдена

---

### Мои поездки (водитель)

**Endpoint:** `GET /trips/my/driver`

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "uuid",
      "from_city": "Москва",
      "to_city": "Санкт-Петербург",
      "departure_date": "2024-03-15",
      "departure_time": "10:00",
      "available_seats": 3,
      "price_per_seat": 1500,
      "status": "active",
      "passengers_count": 1
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

## REQUESTS — Заявки

### Отправить заявку на поездку

**Endpoint:** `POST /trips/{trip_id}/requests`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "seats_requested": 2,
  "message": "Еду с другом, можем взять 2 места"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "trip_id": "uuid",
  "passenger_id": "uuid",
  "passenger": {
    "id": "uuid",
    "name": "Пётр",
    "avatar_url": null,
    "rating": 4.5
  },
  "seats_requested": 2,
  "message": "Еду с другом, можем взять 2 места",
  "status": "pending",
  "created_at": "2024-03-01T10:00:00Z"
}
```

**Errors:**
- `401` — Не авторизован
- `404` — Поездка не найдена
- `409` — Заявка уже отправлена

---

### Получить мои заявки (пассажир)

**Endpoint:** `GET /requests/my`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `status` | string | Нет | Фильтр: pending, confirmed, rejected |
| `page` | integer | Нет | Номер страницы |
| `page_size` | integer | Нет | Размер страницы |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "uuid",
      "trip_id": "uuid",
      "trip": {
        "id": "uuid",
        "from_city": "Москва",
        "to_city": "Санкт-Петербург",
        "departure_date": "2024-03-15",
        "departure_time": "10:00",
        "driver_name": "Иван"
      },
      "seats_requested": 2,
      "status": "pending",
      "created_at": "2024-03-01T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

### Получить заявки на поездку (водитель)

**Endpoint:** `GET /trips/{trip_id}/requests`

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "uuid",
      "passenger_id": "uuid",
      "passenger": {
        "id": "uuid",
        "name": "Пётр",
        "avatar_url": null,
        "rating": 4.5,
        "phone": "+79001234567"
      },
      "seats_requested": 2,
      "message": "Еду с другом",
      "status": "pending",
      "created_at": "2024-03-01T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

**Errors:**
- `401` — Не авторизован
- `403` — Не владелец поездки
- `404` — Поездка не найдена

---

### Подтвердить/отклонить заявку

**Endpoint:** `PUT /requests/{request_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "status": "confirmed"
}
```

**Status values:** `confirmed` | `rejected`

**Response (200 OK):**
```json
{
  "id": "uuid",
  "trip_id": "uuid",
  "passenger_id": "uuid",
  "seats_requested": 2,
  "status": "confirmed",
  "created_at": "2024-03-01T10:00:00Z",
  "updated_at": "2024-03-01T12:00:00Z"
}
```

**Errors:**
- `401` — Не авторизован
- `403` — Нет прав на изменение
- `404` — Заявка не найдена

---

## USERS — Пользователи

### Получить профиль пользователя

**Endpoint:** `GET /users/{user_id}`

**Response (200 OK):**
```json
{
  "id": "uuid",
  "name": "Иван",
  "phone": "+79001234567",
  "avatar_url": "https://...",
  "rating": 4.8,
  "trips_as_driver": 15,
  "trips_as_passenger": 23,
  "member_since": "2024-01-01T10:00:00Z"
}
```

---

### Обновить профиль

**Endpoint:** `PUT /users/{user_id}`

**Headers:** `Authorization: Bearer <token>`

**Request Body:**
```json
{
  "name": "Иван",
  "phone": "+79001234567"
}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "name": "Иван",
  "phone": "+79001234567",
  "avatar_url": null,
  "rating": 4.8,
  "created_at": "2024-01-01T10:00:00Z"
}
```

**Errors:**
- `401` — Не авторизован
- `403` — Нет прав изменение

---

### Получить на поездки пользователя

**Endpoint:** `GET /users/{user_id}/trips`

**Query Parameters:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `role` | string | Нет | driver / passenger |
| `page` | integer | Нет | Номер страницы |
| `page_size` | integer | Нет | Размер страницы |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "uuid",
      "role": "driver",
      "from_city": "Москва",
      "to_city": "Санкт-Петербург",
      "departure_date": "2024-03-15",
      "departure_time": "10:00",
      "status": "completed"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1
}
```

---

## NOTIFICATIONS — Уведомления

### Получить уведомления

**Endpoint:** `GET /notifications`

**Headers:** `Authorization: Bearer <token>`

**Query Parameters:**

| Параметр | Тип | Обязательный | Описание |
|----------|-----|--------------|----------|
| `is_read` | boolean | Нет | Фильтр по статусу прочтения |
| `page` | integer | Нет | Номер страницы |
| `page_size` | integer | Нет | Размер страницы |

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "uuid",
      "type": "request_confirmed",
      "title": "Заявка подтверждена",
      "message": "Водитель подтвердил вашу заявку на поездку",
      "is_read": false,
      "related_trip_id": "uuid",
      "related_request_id": "uuid",
      "created_at": "2024-03-01T10:00:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 20,
  "pages": 1,
  "unread_count": 1
}
```

---

### Прочитать уведомление

**Endpoint:** `PUT /notifications/{notification_id}/read`

**Headers:** `Authorization: Bearer <token>`

**Response (200 OK):**
```json
{
  "id": "uuid",
  "type": "request_confirmed",
  "title": "Заявка подтверждена",
  "message": "Водитель подтвердил вашу заявку на поездку",
  "is_read": true,
  "related_trip_id": "uuid",
  "created_at": "2024-03-01T10:00:00Z"
}
```

---

### Прочитать все уведомления

**Endpoint:** `PUT /notifications/read-all`

**Headers:** `Authorization: Bearer <token>`

**Response:** `204 No Content`

---

## Коды ошибок

### Стандартные HTTP коды

| Код | Название | Описание |
|-----|----------|----------|
| `200` | OK | Успешный запрос |
| `201` | Created | Ресурс создан |
| `204` | No Content | Успешный запрос без возврата данных |
| `400` | Bad Request | Некорректный запрос |
| `401` | Unauthorized | Требуется аутентификация |
| `403` | Forbidden | Нет доступа |
| `404` | Not Found | Ресурс не найден |
| `409` | Conflict | Конфликт (дублирование) |
| `422` | Unprocessable Entity | Ошибка валидации |
| `500` | Internal Server Error | Внутренняя ошибка сервера |

### Формат ошибки валидации (422)

```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

### Формат ошибки приложения (4xx)

```json
{
  "detail": "Поездка не найдена"
}
```

---

## Типы уведомлений

| Type | Title | Описание |
|------|-------|----------|
| `request_received` | Новая заявка | Пассажир отправил заявку на поездку |
| `request_confirmed` | Заявка подтверждена | Водитель подтвердил заявку |
| `request_rejected` | Заявка отклонена | Водитель отклонил заявку |
| `trip_cancelled` | Поездка отменена | Водитель отменил поездку |

---

## Версионирование

- API версионируется через URL: `/api/v1/...`
- Текущая версия: `v1`
- Документация Swagger: `/docs`
- ReDoc: `/redoc`
