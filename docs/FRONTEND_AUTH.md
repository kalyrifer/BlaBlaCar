# Frontend Auth — Поведение клиента

> Версия: 1.0 (MVP)

## 1. Хранение токена

### Решение: httpOnly Cookie

Токен хранится в httpOnly cookie, что означает:
- JavaScript не имеет доступа к токену (защита от XSS)
- Браузер автоматически отправляет токен с каждым запросом
- Токен автоматически удаляется при закрытии браузера (без remember me)

### Реализация

```javascript
// API клиент автоматически добавляет cookie
// Пример с fetch:
const apiClient = axios.create({
  baseURL: '/api',
  withCredentials: true, // Важно для отправки cookies
});

// Или с fetch:
fetch('/api/auth/me', {
  credentials: 'include' // Включить cookies
});
```

---

## 2. Состояние авторизации

### Глобальное состояние (Store)

```typescript
interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  isLoading: boolean;
}

// Пример с React Context / Zustand:
const useAuth = create((set) => ({
  isAuthenticated: false,
  user: null,
  isLoading: true,
  
  setUser: (user) => set({ user, isAuthenticated: true, isLoading: false }),
  logout: () => set({ user: null, isAuthenticated: false, isLoading: false }),
}));
```

### Проверка авторизации при загрузке

```typescript
// Приложение загружается:
useEffect(() => {
  checkAuth();
}, []);

async function checkAuth() {
  try {
    const response = await apiClient.get('/auth/me');
    authStore.setUser(response.data);
  } catch (error) {
    authStore.logout();
  }
}
```

---

## 3. Protected Routes (Защищённые маршруты)

### Пример реализации

```typescript
function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return children;
}

// Использование в роутинге:
<Route path="/trips/new" element={
  <ProtectedRoute>
    <CreateTripPage />
  </ProtectedRoute>
} />
```

---

## 4. Редиректы

### Логика редиректов

| Событие | Условие | Результат |
|---------|---------|-----------|
| Неавторизованный на `/trips/new` | `!isAuthenticated` | → `/login?redirect=/trips/new` |
| Неавторизованный на `/my-trips` | `!isAuthenticated` | → `/login?redirect=/my-trips` |
| Авторизованный на `/login` | `isAuthenticated` | → `/` |
| Авторизованный на `/register` | `isAuthenticated` | → `/` |
| Успешный login | | → `redirect` или `/` |
| Успешный register | | → `/` (создан аккаунт) |
| Выход | | → `/` |

### Пример обработки редиректа

```typescript
// LoginPage
function LoginPage() {
  const navigate = useNavigate();
  const searchParams = new URLSearchParams(useLocation().search);
  const redirect = searchParams.get('redirect') || '/';
  
  async function handleLogin(credentials) {
    await apiClient.post('/auth/login', credentials);
    navigate(redirect);
  }
}
```

---

## 5. Обработка ошибок токена

### Сценарии ошибок

| Код | Сообщение | Действие |
|-----|-----------|----------|
| 401 Unauthorized | "Invalid credentials" | Показать ошибку формы |
| 401 Token expired | "Session expired" | Очистить store, редирект на login |
| 401 Invalid token | "Please log in again" | Очистить store, редирект на login |
| 403 Forbidden | "Access denied" | Показать 403 страницу |

### Интерцептор axios

```typescript
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Токен истёк или недействителен
      authStore.logout();
      
      // Сохраняем текущий путь для редиректа
      const currentPath = window.location.pathname;
      window.location.href = `/login?redirect=${currentPath}`;
    }
    return Promise.reject(error);
  }
);
```

---

## 6. Logout (Выход)

###流程

```typescript
async function handleLogout() {
  try {
    await apiClient.post('/auth/logout');
  } catch (error) {
    // Игнорируем ошибку
  } finally {
    // Очищаем локальное состояние
    authStore.logout();
    
    // Редирект на главную
    navigate('/');
  }
}
```

### Кнопка выхода

```tsx
// В хедере:
{isAuthenticated && (
  <button onClick={handleLogout}>Выйти</button>
)}
```

---

## 7. Auth API вызовы

### Регистрация

```typescript
interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  phone: string;
}

async function register(data: RegisterRequest) {
  const response = await apiClient.post('/auth/register', data);
  // Токен уже установлен в cookie сервером
  return response.data;
}
```

### Вход

```typescript
interface LoginRequest {
  email: string;
  password: string;
}

async function login(data: LoginRequest) {
  const response = await apiClient.post('/auth/login', data);
  // Токен уже установлен в cookie сервером
  return response.data.user;
}
```

### Получение текущего пользователя

```typescript
async function getCurrentUser() {
  const response = await apiClient.get('/auth/me');
  return response.data;
}
```

---

## 8. UI состояния

### Форма входа

```tsx
function LoginForm() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  async function handleSubmit(credentials) {
    setIsLoading(true);
    setError(null);
    
    try {
      await login(credentials);
    } catch (err) {
      if (err.response?.status === 401) {
        setError('Неверный email или пароль');
      } else {
        setError('Произошла ошибка. Попробуйте позже.');
      }
    } finally {
      setIsLoading(false);
    }
  }
}
```

### Кнопки по состоянию авторизации

```tsx
// В хедере:
{isAuthenticated ? (
  <>
    <Link to="/my-trips">Мои поездки</Link>
    <Link to="/notifications">
      Уведомления
      {unreadCount > 0 && <span className="badge">{unreadCount}</span>}
    </Link>
    <Link to="/profile">Профиль</Link>
    <button onClick={handleLogout}>Выйти</button>
  </>
) : (
  <>
    <Link to="/login">Войти</Link>
    <Link to="/register">Регистрация</Link>
  </>
)}
```

---

## 9. Refresh Token (Не требуется для MVP)

Для MVP используем простую схему:
- Access token срок жизни: 24 часа
- При истечении → пользователь перелогинивается
- Refresh token не реализуем

---

## 10. Protected Actions (Защищённые действия)

### Пример проверки перед действием

```typescript
async function handleRequestTrip(tripId: string) {
  if (!isAuthenticated) {
    navigate(`/login?redirect=/trips/${tripId}`);
    return;
  }
  
  // Показать модалку заявки
  setShowModal(true);
}
```

### Кнопка "Отправить заявку"

```tsx
<button 
  onClick={handleRequestTrip}
  disabled={!isAuthenticated}
>
  {!isAuthenticated 
    ? 'Войдите, чтобы отправить заявку' 
    : 'Отправить заявку'
  }
</button>
```
