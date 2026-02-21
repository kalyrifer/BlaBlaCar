import { useEffect, useState } from 'react';
import { api } from '../services/api';
import { Notification } from '../types';

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNotifications();
  }, []);

  const loadNotifications = async () => {
    try {
      const data = await api.getNotifications();
      setNotifications(data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (id: number) => {
    try {
      await api.markNotificationRead(id);
      setNotifications(notifications.map(n => 
        n.id === id ? { ...n, is_read: true } : n
      ));
    } catch (error) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="notifications-page">
      <h1>Уведомления</h1>
      
      {notifications.length === 0 ? (
        <p className="empty-state">Уведомлений пока нет</p>
      ) : (
        <div className="notifications-list">
          {notifications.map(notification => (
            <div 
              key={notification.id} 
              className={`notification ${!notification.is_read ? 'unread' : ''}`}
              onClick={() => !notification.is_read && markAsRead(notification.id)}
            >
              <p>{notification.message}</p>
              <span className="notification-date">
                {new Date(notification.created_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
