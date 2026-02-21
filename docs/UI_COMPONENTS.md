# UI Компоненты и их API

> Версия: 1.0 (MVP)

---

## 1. SearchForm (Форма поиска)

**Расположение:** Главная страница, хедер на странице результатов

### Props

```typescript
interface SearchFormProps {
  initialFrom?: string;
  initialTo?: string;
  initialDate?: string;
  onSearch: (params: SearchParams) => void;
  isLoading?: boolean;
}

interface SearchParams {
  from_city: string;
  to_city: string;
  date: string; // YYYY-MM-DD
}
```

### События

| Событие | Параметры | Описание |
|---------|-----------|----------|
| `onSearch` | `{from_city, to_city, date}` | Сабмит формы |

### Состояния

- `idle` — ожидание ввода
- `loading` — загрузка (показывается скелетон)
- `error` — ошибка валидации

---

## 2. TripCard (Карточка поездки)

**Расположение:** Список на странице `/trips`

### Props

```typescript
interface TripCardProps {
  trip: Trip;
  onClick: (tripId: string) => void;
}

interface Trip {
  id: string;
  from_city: string;
  to_city: string;
  departure_date: string;
  departure_time: string;
  available_seats: number;
  price_per_seat: number;
  driver: {
    id: string;
    name: string;
    avatar_url?: string;
    rating?: number;
  };
}
```

### Визуальные элементы

```
┌─────────────────────────────────────────┐
│ 🚗 Иван ★ 4.8                           │
├─────────────────────────────────────────┤
│ Москва → Санкт-Петербург                 │
│ 15 марта, 10:00                         │
│ 3 места · 1500 ₽                        │
└─────────────────────────────────────────┘
```

### События

| Событие | Параметры | Описание |
|---------|-----------|----------|
| `onClick` | `tripId` | Клик на карточку |

---

## 3. TripDetails (Детали поездки)

**Расположение:** Страница `/trips/:id`

### Props

```typescript
interface TripDetailsProps {
  trip: TripFull;
  isOwner: boolean;
  userHasRequest?: RequestStatus;
  onRequest: (seats: number, message: string) => void;
  onBack: () => void;
}

interface TripFull extends Trip {
  description?: string;
  status: 'active' | 'completed' | 'cancelled';
  created_at: string;
  driver: {
    id: string;
    name: string;
    phone: string;
    avatar_url?: string;
    rating?: number;
    created_at: string;
  };
}

type RequestStatus = 'pending' | 'confirmed' | 'rejected' | null;
```

### Кнопки (по состоянию)

| Состояние | Кнопка |
|-----------|--------|
| Авторизован, не водитель, нет заявки | "Отправить заявку" |
| Авторизован, не водитель, заявка pending | "Ожидает подтверждения" (disabled) |
| Авторизован, не водитель, заявка confirmed | "Заявка подтверждена" (disabled) |
| Водитель (isOwner) | "Редактировать", "Отменить" |
| Не авторизован | "Войдите, чтобы отправить заявку" |

---

## 4. CreateTripForm (Форма создания поездки)

**Расположение:** Страница `/trips/new`

### Props

```typescript
interface CreateTripFormProps {
  onSubmit: (data: CreateTripData) => Promise<void>;
  onCancel: () => void;
  isLoading?: boolean;
}

interface CreateTripData {
  from_city: string;
  to_city: string;
  departure_date: string;
  departure_time: string;
  available_seats: number;
  price_per_seat: number;
  description?: string;
}
```

### Поля формы

| Поле | Тип | Валидация | Обязательно |
|------|-----|-----------|-------------|
| from_city | text | min 2 символа | Да |
| to_city | text | min 2 символа | Да |
| departure_date | date | >= сегодня | Да |
| departure_time | time | | Да |
| available_seats | number | 1-8 | Да |
| price_per_seat | number | >= 0 | Да |
| description | textarea | max 500 | Нет |

---

## 5. RequestModal (Модалка заявки)

**Триггер:** Клик "Отправить заявку" на TripDetails

### Props

```typescript
interface RequestModalProps {
  isOpen: boolean;
  trip: Trip;
  onSubmit: (seats: number, message: string) => Promise<void>;
  onClose: () => void;
  isLoading?: boolean;
}
```

### Содержимое

```
┌─────────────────────────────────────┐
│ Заявка на поездку                   │
├─────────────────────────────────────┤
│ Москва → Санкт-Петербург             │
│ 3 места доступно                    │
│                                     │
│ Количество мест: [1] [2] [3]        │
│                                     │
│ Сообщение водителю (опционально):   │
│ [________________________]          │
│                                     │
│ [Отмена]  [Отправить заявку]        │
└─────────────────────────────────────┘
```

---

## 6. NotificationItem (Элемент уведомления)

**Расположение:** Список на странице `/notifications`

### Props

```typescript
interface NotificationItemProps {
  notification: Notification;
  onRead: (id: string) => void;
  onClick: (notification: Notification) => void;
}

interface Notification {
  id: string;
  type: 'request_received' | 'request_confirmed' | 'request_rejected' | 'trip_cancelled';
  title: string;
  message: string;
  is_read: boolean;
  related_trip_id?: string;
  related_request_id?: string;
  created_at: string;
}
```

### Визуальные элементы

- Непрочитанные — жирный текст, синяя точка
- Тип иконки по `type`:
  - `request_received` — 📥
  - `request_confirmed` — ✅
  - `request_rejected` — ❌
  - `trip_cancelled` — 🚫

---

## 7. UserAvatar (Аватар пользователя)

**Props**

```typescript
interface UserAvatarProps {
  name: string;
  avatar_url?: string;
  size?: 'sm' | 'md' | 'lg';
  rating?: number;
}
```

### Размеры

| Size | Размер | Применение |
|------|--------|------------|
| sm | 32px | Список, карточки |
| md | 48px | Профиль |
| lg | 96px | Детальный профиль |

---

## 8. Button (Кнопка)

**Props**

```typescript
interface ButtonProps {
  variant: 'primary' | 'secondary' | 'outline' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
  type?: 'button' | 'submit';
  children: React.ReactNode;
}
```

---

## 9. Input (Поле ввода)

**Props**

```typescript
interface InputProps {
  label?: string;
  error?: string;
  type: 'text' | 'email' | 'password' | 'date' | 'time' | 'number' | 'tel';
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
}
```

---

## 10. AuthForm (Форма авторизации)

### LoginForm Props

```typescript
interface LoginFormProps {
  onSubmit: (email: string, password: string) => Promise<void>;
  isLoading?: boolean;
}
```

### RegisterForm Props

```typescript
interface RegisterFormProps {
  onSubmit: (data: RegisterData) => Promise<void>;
  isLoading?: boolean;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
  phone: string;
}
```

---

## 11. MyTripsList (Список моих поездок)

### Props

```typescript
interface MyTripsListProps {
  trips: MyTrip[];
  role: 'driver' | 'passenger';
  onTripClick: (tripId: string) => void;
}

interface MyTrip {
  id: string;
  from_city: string;
  to_city: string;
  departure_date: string;
  departure_time: string;
  status: string;
  passengers_count?: number; // для водителя
  request_status?: 'pending' | 'confirmed' | 'rejected'; // для пассажира
}
```

---

## 12. ProfileCard (Профиль пользователя)

### Props

```typescript
interface ProfileCardProps {
  user: UserProfile;
  isOwn?: boolean;
  onEdit?: () => void;
  onTripClick?: (tripId: string) => void;
}

interface UserProfile {
  id: string;
  name: string;
  phone?: string;
  avatar_url?: string;
  rating?: number;
  trips_as_driver: number;
  trips_as_passenger: number;
  member_since: string;
}
```
