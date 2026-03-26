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
