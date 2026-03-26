import { Link } from 'react-router-dom';
import type { ConversationListItem } from '../../types';

interface ChatListProps {
  conversations: ConversationListItem[];
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
