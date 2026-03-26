# Промпт 5: Frontend — Компоненты UI чата

## Задача

Создать React компоненты для отображения чата.

## Требования к проекту

- Проект: RoadMate — React 18 + TypeScript
- Используется: React Router v6, CSS модули или глобальные стили
- Компоненты должны быть в папке `frontend/src/components/chat/`

## Справочная информация

Пример существующего компонента:

```tsx
// frontend/src/components/ui/Button.tsx
import { ButtonHTMLAttributes } from 'react';
import './Button.css';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary';
}

export function Button({ variant = 'primary', className, ...props }: ButtonProps) {
  return (
    <button className={`btn btn-${variant} ${className || ''}`} {...props} />
  );
}
```

Пример использования useAuthStore:

```tsx
import { useAuthStore } from '../stores/auth';
const user = useAuthStore((state) => state.user);
```

## Задание

### 1. Создать компонент списка чатов

Создать файл `frontend/src/components/chat/ChatList.tsx`:

```tsx
import { Link } from 'react-router-dom';
import type { Conversation } from '../../types';

interface ChatListProps {
  conversations: Conversation[];
}

export function ChatList({ conversations }: ChatListProps) {
  if (conversations.length === 0) {
    return (
      <div className="empty-state" style={{ padding: '40px', textAlign: 'center' }}>
        <p style={{ fontSize: '18px', color: '#6b7280', marginBottom: '8px' }}>
          У вас пока нет чатов
        </p>
        <p style={{ color: '#9ca3af' }}>
          Чаты появятся после подтверждения заявки на поездку
        </p>
      </div>
    );
  }

  return (
    <div className="chat-list">
      {conversations.map((conv) => (
        <Link
          key={conv.id}
          to={`/messages/${conv.id}`}
          className="chat-list-item"
          style={{
            display: 'flex',
            alignItems: 'center',
            padding: '16px',
            borderBottom: '1px solid #e5e7eb',
            textDecoration: 'none',
            color: 'inherit',
          }}
        >
          <div
            className="chat-list-avatar"
            style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              background: '#00a8e8',
              color: 'white',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: '20px',
              fontWeight: 600,
              marginRight: '12px',
            }}
          >
            {conv.other_user_name.charAt(0).toUpperCase()}
          </div>
          <div style={{ flex: 1, minWidth: 0 }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
              <span style={{ fontWeight: 600, color: '#1a1a2e' }}>{conv.other_user_name}</span>
              {conv.last_message_time && (
                <span style={{ fontSize: '12px', color: '#9ca3af' }}>
                  {new Date(conv.last_message_time).toLocaleDateString('ru-RU')}
                </span>
              )}
            </div>
            <div style={{ fontSize: '13px', color: '#6b7280', marginBottom: '4px' }}>
              {conv.trip_from_city} → {conv.trip_to_city}
            </div>
            {conv.last_message && (
              <div style={{ fontSize: '14px', color: '#9ca3af', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                {conv.last_message}
              </div>
            )}
          </div>
          {conv.unread_count > 0 && (
            <div
              style={{
                background: '#00a8e8',
                color: 'white',
                borderRadius: '12px',
                padding: '2px 8px',
                fontSize: '12px',
                fontWeight: 600,
              }}
            >
              {conv.unread_count}
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}
```

### 2. Создать компонент пузыря сообщения

Создать файл `frontend/src/components/chat/MessageBubble.tsx`:

```tsx
import type { Message } from '../../types';
import { useAuthStore } from '../../stores/auth';

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const user = useAuthStore((state) => state.user);
  const isOwn = message.sender_id === user?.id;

  return (
    <div
      className={`message-bubble ${isOwn ? 'message-own' : 'message-other'}`}
      style={{
        maxWidth: '70%',
        padding: '12px 16px',
        borderRadius: '16px',
        wordWrap: 'break-word',
        alignSelf: isOwn ? 'flex-end' : 'flex-start',
        background: isOwn ? '#00a8e8' : '#f3f4f6',
        color: isOwn ? 'white' : '#1a1a2e',
        borderBottomRightRadius: isOwn ? '4px' : '16px',
        borderBottomLeftRadius: isOwn ? '16px' : '4px',
      }}
    >
      <div style={{ marginBottom: '4px' }}>{message.content}</div>
      <div style={{ fontSize: '11px', opacity: 0.7, textAlign: 'right' }}>
        {new Date(message.created_at).toLocaleTimeString('ru-RU', {
          hour: '2-digit',
          minute: '2-digit',
        })}
      </div>
    </div>
  );
}
```

### 3. Создать компонент окна чата

Создать файл `frontend/src/components/chat/ChatWindow.tsx`:

```tsx
import { useState, useRef, useEffect } from 'react';
import { chatApi } from '../../services/api';
import { MessageBubble } from './MessageBubble';
import type { Message } from '../../types';

interface ChatWindowProps {
  conversationId: string;
  messages: Message[];
  onNewMessage: (message: Message) => void;
}

export function ChatWindow({ conversationId, messages, onNewMessage }: ChatWindowProps) {
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!newMessage.trim() || sending) return;
    
    setSending(true);
    try {
      const response = await chatApi.sendMessage(conversationId, newMessage.trim());
      onNewMessage(response.data);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 200px)' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      
      <div style={{ display: 'flex', gap: '12px', padding: '16px', borderTop: '1px solid #e5e7eb', background: 'white' }}>
        <textarea
          style={{
            flex: 1,
            padding: '12px',
            border: '2px solid #e5e7eb',
            borderRadius: '12px',
            resize: 'none',
            fontFamily: 'inherit',
          }}
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Введите сообщение..."
          rows={2}
        />
        <button
          onClick={handleSend}
          disabled={sending || !newMessage.trim()}
          style={{
            padding: '12px 24px',
            background: sending || !newMessage.trim() ? '#9ca3af' : '#00a8e8',
            color: 'white',
            border: 'none',
            borderRadius: '12px',
            cursor: sending || !newMessage.trim() ? 'not-allowed' : 'pointer',
            fontWeight: 600,
          }}
        >
          {sending ? '...' : 'Отправить'}
        </button>
      </div>
    </div>
  );
}
```

## Критерии приёмки

- [ ] Папка `frontend/src/components/chat/` создана
- [ ] Файл `ChatList.tsx` отображает список чатов с мета-информацией
- [ ] Файл `MessageBubble.tsx` отображает сообщения с разделением на свои/чужие
- [ ] Файл `ChatWindow.tsx` позволяет отправлять сообщения и автоматически скроллит
- [ ] Компоненты используют inline стили (как в существующих компонентах проекта)
- [ ] Компоненты правильно используют useAuthStore для определения своего сообщения