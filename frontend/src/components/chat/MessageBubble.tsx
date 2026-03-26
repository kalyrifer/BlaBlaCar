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
