# Промпт 4: Frontend — Типы и API сервис

## Задача

Добавить TypeScript типы и API методы для системы чата на фронтенде.

## Требования к проекту

- Проект: RoadMate — React 18 + TypeScript + Vite
- Используется: axios для HTTP запросов, Zustand для стейта

## Справочная информация

Пример существующего API в проекте:

```typescript
// frontend/src/services/api.ts
import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: '/api',
  withCredentials: true,
});

export const tripsApi = {
  getById: (id: string) => axiosInstance.get(`/trips/${id}`),
  create: (data: any) => axiosInstance.post('/trips', data),
};
```

Пример типов в проекте:

```typescript
// frontend/src/types/index.ts
export interface User {
  id: string;
  name: string;
  email: string;
}

export interface Trip {
  id: string;
  from_city: string;
  to_city: string;
}
```

## Задание

### 1. Добавить типы чата

Добавить в конец файла `frontend/src/types/index.ts`:

```typescript
// Chat types
export interface Conversation {
  id: string;
  trip_id: string;
  other_user_id: string;
  other_user_name: string;
  trip_from_city: string;
  trip_to_city: string;
  last_message?: string;
  last_message_time?: string;
  unread_count: number;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

export interface ConversationDetail {
  id: string;
  trip_id: string;
  driver_id: string;
  passenger_id: string;
}
```

### 2. Добавить API методы

Добавить в файл `frontend/src/services/api.ts`:

```typescript
// Chat API
export const chatApi = {
  // Get all conversations for current user
  getConversations: () => 
    axiosInstance.get<Conversation[]>('/chat/conversations'),
  
  // Get or create conversation for a trip
  getOrCreateConversation: (tripId: string) =>
    axiosInstance.post<ConversationDetail>(`/chat/trips/${trip_id}/conversation`),
  
  // Get messages in a conversation
  getMessages: (conversationId: string, skip = 0, limit = 50) =>
    axiosInstance.get<Message[]>(
      `/chat/conversations/${conversationId}/messages`,
      { params: { skip, limit } }
    ),
  
  // Send a message
  sendMessage: (conversationId: string, content: string) =>
    axiosInstance.post<Message>(
      `/chat/conversations/${conversationId}/messages`,
      { content }
    ),
};

// Обновить экспорт api объекта (добавить в конец объекта api):
export const api = {
  // ... существующие методы
  // Chat
  getConversations: chatApi.getConversations,
  getOrCreateConversation: chatApi.getOrCreateConversation,
  getMessages: chatApi.getMessages,
  sendMessage: chatApi.sendMessage,
};
```

## Критерии приёмки

- [ ] Типы Conversation, Message, ConversationDetail добавлены в types/index.ts
- [ ] Объект chatApi создан с четырьмя методами
- [ ] API методы добавлены в общий объект api
- [ ] Типы используют string для ID (как в существующих типах проекта)
- [ ] Параметры имеют значения по умолчанию для пагинации