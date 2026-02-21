# Спецификация аутентификации

> Версия: 1.0 (MVP)

## 1. Выбор механизма аутентификации

### Решение: JWT (JSON Web Tokens)

| Критерий | Выбор | Обоснование |
|----------|-------|-------------|
| **Тип токена** | JWT Access Token | Stateless, масштабируемость, стандарт |
| **Хранение на клиенте** | httpOnly Cookie | Защита от XSS |
| **Срок жизни токена** | 24 часа (access) | Баланс безопасности/удобства для MVP |
| **Refresh Token** | Не требуется | Упрощение MVP |

## 2. Flow аутентификации

### Регистрация

```
┌─────────┐                           ┌─────────┐
│ Client  │                           │ Server  │
└────┬────┘                           └────┬────┘
     │                                      │
     │ POST /api/auth/register              │
     │ { email, password, name, phone }    │
     │─────────────────────────────────────>│
     │                                      │
     │ 201 Created                          │
     │ { user, access_token }               │
     │<─────────────────────────────────────│
     │                                      │
     │ Сохранить token в httpOnly cookie   │
     │                                      │
```

### Вход

```
┌─────────┐                           ┌─────────┐
│ Client  │                           │ Server  │
└────┬────┘                           └────┬────┘
     │                                      │
     │ POST /api/auth/login                 │
     │ { email, password }                  │
     │─────────────────────────────────────>│
     │                                      │
     │ 200 OK                               │
     │ { access_token, user }               │
     │<─────────────────────────────────────│
     │                                      │
     │ Сохранить token в httpOnly cookie   │
     │                                      │
```

### Защищённый запрос

```
┌─────────┐                           ┌─────────┐
│ Client  │                           │ Server  │
└────┬────┘                           └────┬────┘
     │                                      │
     │ GET /api/trips                       │
     │ Cookie: access_token=...            │
     │─────────────────────────────────────│
     │                                      │
     │ Проверить токен, извлечь user_id    │
     │                                      │
     │ 200 OK                              │
     │ { trips: [...] }                     │
     │<─────────────────────────────────────│
     │                                      │
```

## 3. Структура JWT токена

### Payload

```json
{
  "sub": "uuid-пользователя",
  "email": "user@example.com",
  "name": "Иван",
  "exp": 1710000000,
  "iat": 1709900000
}
```

### Secret Key

- **Алгоритм:** HS256
- **Secret:** конфигурируется через переменную окружения `JWT_SECRET_KEY`
- **Значение по умолчанию для dev:** `dev-secret-key-change-in-production`

## 4. Хранение токена

### Решение: httpOnly Cookie

** на клиентеПреимущества:**
- Защита от XSS атак (токен недоступен через JavaScript)
- Автоматическая отправка с каждым запросом
- Не требуется手动ное управление токеном

**Недостатки:**
- Нельзя использовать для запросов с других доменов (CORS)
- Требует HTTPS в production

### Frontend интеграция

```javascript
// При регистрации/логине сервер устанавливает cookie
// Последующие запросы автоматически включают cookie

// При выходе - сервер очищает cookie
```

### Server-side cookie установка

```python
# FastAPI пример
response = JSONResponse({
    "user": user_data,
    "access_token": access_token
})
response.set_cookie(
    key="access_token",
    value=access_token,
    httponly=True,
    secure=True,  # True в production
    samesite="lax",
    max_age=86400  # 24 часа
)
return response
```

## 5. Logout (Выход)

```
┌─────────┐                           ┌─────────┐
│ Client  │                           │ Server  │
└────┬────┘                           └────┬────┘
     │                                      │
     │ POST /api/auth/logout                │
     │─────────────────────────────────────>│
     │                                      │
     │ Очистить cookie                      │
     │ 204 No Content                       │
     │<─────────────────────────────────────│
     │                                      │
     │ Очистить локальное состояние         │
     │                                      │
```

## 6. Защита пароля

### Хеширование

- **Алгоритм:** bcrypt
- **Work factor:** 10 (по умолчанию)

### Валидация пароля

- Минимальная длина: 8 символов
- Требования: нет строгих требований для MVP

## 7. Endpoints аутентификации

| Endpoint | Метод | Описание |
|----------|-------|----------|
| `/api/auth/register` | POST | Регистрация нового пользователя |
| `/api/auth/login` | POST | Вход пользователя |
| `/api/auth/logout` | POST | Выход пользователя |
| `/api/auth/me` | GET | Получить текущего пользователя |

## 8. Обработка ошибок

| Код | Сообщение | Описание |
|-----|-----------|----------|
| `401` | `Invalid credentials` | Неверный email или пароль |
| `401` | `Token expired` | Срок токена истёк |
| `401` | `Invalid token` | Токен повреждён или поддельный |
| `400` | `Email already registered` | Email уже используется |
| `422` | `Invalid email format` | Некорректный формат email |

## 9. Безопасность

### Production рекомендации

1. **HTTPS** — обязательно в production
2. **JWT_SECRET_KEY** — сложная случайная строка
3. **Secure cookie** — `secure=True` в production
4. **CORS** — настроить допустимые источники

### Development

- `JWT_SECRET_KEY`: `dev-secret-key-change-in-production`
- `secure=False` для cookie
- Логирование отладочной информации

## 10. Тестирование

### Unit тесты

```python
# Тест генерации токена
def test_create_access_token():
    token = create_access_token("user-id", "user@example.com")
    assert token is not None
    assert isinstance(token, str)

# Тест верификации токена
def test_verify_token():
    token = create_access_token("user-id", "user@example.com")
    payload = verify_token(token)
    assert payload["sub"] == "user-id"
```

### Integration тесты

- Регистрация с корректными данными
- Регистрация с дублирующимся email
- Вход с неверным паролем
- Защищённый endpoint без токена
- Защищённый endpoint с истёкшим токеном
