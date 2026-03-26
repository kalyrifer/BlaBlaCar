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
      setMessages(response.data.items);
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
