# Промпт 6: Frontend — Страницы и маршрутизация

## Задача

Создать страницы сообщений и добавить маршрутизацию.

## Требования к проекту

- Проект: RoadMate — React 18 + React Router v6
- Используется: lazy loading для страниц, ProtectedRoute для авторизованных маршрутов

## Справочная информация

Пример lazy loading страницы:

```tsx
// frontend/src/App.tsx
const HomePage = lazy(() => import('./pages/HomePage'));

function App() {
  return (
    <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/" element={<HomePage />} />
      </Routes>
    </Suspense>
  );
}
```

Пример ProtectedRoute:

```tsx
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated } = useAuthStore();
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}
```

## Задание

### 1. Создать страницу списка сообщений

Создать файл `frontend/src/pages/MessagesPage.tsx`:

```tsx
import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ChatList } from '../components/chat/ChatList';
import type { Conversation } from '../types';

export default function MessagesPage() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await api.getConversations();
        setConversations(response.data);
      } catch (error) {
        console.error('Error fetching conversations:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchConversations();
  }, []);

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        Загрузка...
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#1a1a2e' }}>
          Сообщения
        </h1>
      </div>
      
      <ChatList conversations={conversations} />
    </div>
  );
}
```

### 2. Создать страницу конкретного чата

Создать файл `frontend/src/pages/ChatPage.tsx`:

```tsx
import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../services/api';
import { ChatWindow } from '../components/chat/ChatWindow';
import type { Message } from '../types';

export default function ChatPage() {
  const { id } = useParams<{ id: string }>();
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchMessages = useCallback(async () => {
    if (!id) return;
    try {
      const response = await api.getMessages(id);
      setMessages(response.data);
    } catch (error) {
      console.error('Error fetching messages:', error);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    fetchMessages();
    
    // Poll for new messages every 5 seconds
    const interval = setInterval(fetchMessages, 5000);
    return () => clearInterval(interval);
  }, [fetchMessages]);

  const handleNewMessage = (message: Message) => {
    setMessages((prev) => [...prev, message]);
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        Загрузка...
      </div>
    );
  }

  if (!id) {
    return <div>Чат не найден</div>;
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <div style={{ padding: '16px', borderBottom: '1px solid #e5e7eb' }}>
        <Link 
          to="/messages" 
          style={{ 
            color: '#00a8e8', 
            textDecoration: 'none',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          ← Назад к сообщениям
        </Link>
      </div>
      
      <ChatWindow
        conversationId={id}
        messages={messages}
        onNewMessage={handleNewMessage}
      />
    </div>
  );
}
```

### 3. Добавить маршруты в App.tsx

Обновить `frontend/src/App.tsx`:

```tsx
import { Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy } from 'react';

// Добавить lazy imports
const MessagesPage = lazy(() => import('./pages/MessagesPage'));
const ChatPage = lazy(() => import('./pages/ChatPage'));

// Добавить в компонент Routes ( внутри <Route path="/" element={<Layout />}> ):
<Route path="messages" element={
  <ProtectedRoute>
    <MessagesPage />
  </ProtectedRoute>
} />
<Route path="messages/:id" element={
  <ProtectedRoute>
    <ChatPage />
  </ProtectedRoute>
} />
```

### 4. Добавить ссылку в навигацию

Обновить `frontend/src/components/Layout.tsx`, добавить в меню навигации:

```tsx
<Link 
  to="/messages" 
  style={{ 
    display: 'flex', 
    alignItems: 'center', 
    gap: '8px',
    padding: '12px 16px',
    color: '#6b7280',
    textDecoration: 'none'
  }}
>
  <span style={{ fontSize: '20px' }}>💬</span>
  <span>Сообщения</span>
</Link>
```

## Критерии приёмки

- [ ] Файл `MessagesPage.tsx` загружает и отображает список чатов
- [ ] Файл `ChatPage.tsx` отображает сообщения и позволяет отправлять новые
- [ ] ChatPage опрашивает сервер каждые 5 секунд для новых сообщений
- [ ] Маршруты `/messages` и `/messages/:id` добавлены в App.tsx
- [ ] Маршруты защищены ProtectedRoute
- [ ] Ссылка на сообщения добавлена в Layout.tsx