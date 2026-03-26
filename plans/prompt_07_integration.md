# Промпт 7: Интеграция чата с поездками

## Задача

Интегрировать чат с существующими функциями поездок.

## Требования к проекту

- Проект: RoadMate — FastAPI + React
- Интеграция с TripPage и автоматическое создание чата при подтверждении заявки

## Справочная информация

Пример существующей страницы поездки:

```tsx
// frontend/src/pages/TripPage.tsx
export default function TripPage() {
  const { id } = useParams<{ id: string }>();
  const { isAuthenticated, user } = useAuthStore();
  // ... загрузка данных поездки
  
  const isOwner = user?.id === trip.driver_id;
  
  return (
    <div>
      {/* Информация о водителе */}
      <div className="trip-driver">
        <h3>{trip.driver.name}</h3>
      </div>
      
      {/* Кнопка бронирования */}
      {isOwner ? (
        <div>Это ваша поездка</div>
      ) : !isAuthenticated ? (
        <Link to={`/login?redirect=/trips/${trip.id}`}>Войдите</Link>
      ) : trip.available_seats > 0 ? (
        <button onClick={() => setShowModal(true)}>Забронировать</button>
      ) : (
        <div>Нет мест</div>
      )}
    </div>
  );
}
```

## Задание

### 1. Добавить кнопку "Написать" на странице поездки

Обновить `frontend/src/pages/TripPage.tsx` — после секции с информацией о водителе добавить:

```tsx
// Добавить импорт Link
import { Link, useNavigate } from 'react-router-dom';

// Добавить состояние для чата и функцию
const [showChat, setShowChat] = useState(false);

const handleOpenChat = async () => {
  try {
    // Получить или создать чат для этой поездки
    const response = await api.getOrCreateConversation(trip.id);
    // Перейти на страницу чата
    navigate(`/messages/${response.data.id}`);
  } catch (error) {
    console.error('Error opening chat:', error);
  }
};

// Добавить после кнопки "Забронировать место" или вместо неё:
{!isOwner && isAuthenticated && trip.status === 'active' && (
  <button 
    onClick={handleOpenChat}
    className="btn btn-secondary"
    style={{ width: '100%', marginTop: '12px' }}
  >
    Написать водителю
  </button>
)}
```

### 2. Добавить автоматическое создание чата при подтверждении заявки

Найти функцию подтверждения заявки в `backend/app/services/request_service.py` и добавить:

```python
async def confirm_request(
    self, 
    request_id: UUID, 
    driver_id: UUID
) -> TripRequest:
    """Confirm a trip request"""
    # ... существующая логика подтверждения ...
    
    # После подтверждения создать чат
    from app.repositories.inmemory.chat_repo import InMemoryChatRepository
    from app.services.chat_service import ChatService
    
    chat_repo = InMemoryChatRepository()
    chat_service = ChatService(chat_repo)
    
    # Получить информацию о поездке
    trip = await self.trip_repo.get_by_id(request.trip_id)
    
    # Создать или получить существующий чат
    await chat_service.get_or_create_conversation(
        trip_id=trip.id,
        driver_id=trip.driver_id,
        passenger_id=request.passenger_id
    )
    
    return request
```

### 3. Добавить обработку ошибок

Убедиться, что API `/chat/trips/{trip_id}/conversation` возвращает понятные ошибки:

- Если поездка не найдена: 404 "Trip not found"
- Если пользователь не участник поездки: 403 "You are not a participant of this trip"
- Если заявка не подтверждена: 403 "You don't have a confirmed request for this trip"

## Критерии приёмки

- [ ] На TripPage добавлена кнопка "Написать водителю"
- [ ] Кнопка видна только для не-владельцев с подтверждёнными заявками
- [ ] При нажатии на кнопку происходит переход в чат
- [ ] При подтверждении заявки автоматически создаётся чат
- [ ] Обработка ошибок работает корректно