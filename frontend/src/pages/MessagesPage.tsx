import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ChatList } from '../components/chat/ChatList';
import type { ConversationListItem } from '../types';

export default function MessagesPage() {
  const [conversations, setConversations] = useState<ConversationListItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchConversations = async () => {
      try {
        const response = await api.getConversations();
        setConversations(response.data.items);
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
          Чаты
        </h1>
      </div>
      
      <ChatList conversations={conversations} />
    </div>
  );
}
