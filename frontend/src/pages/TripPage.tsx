import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { tripsApi, api } from '../services/api';
import { useAuthStore } from '../stores/auth';
import type { Trip } from '../types';

export default function TripPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { isAuthenticated, user } = useAuthStore();
  const [trip, setTrip] = useState<Trip | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [seats, setSeats] = useState(1);
  const [message, setMessage] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    const fetchTrip = async () => {
      if (!id) return;
      try {
        const response = await tripsApi.getById(id);
        setTrip(response.data);
      } catch (error) {
        console.error('Error fetching trip:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrip();
  }, [id]);

  const handleRequest = async () => {
    if (!id) return;
    setSubmitting(true);
    try {
      await tripsApi.createRequest(id, { seats_requested: seats, message: message || undefined });
      setShowModal(false);
      navigate('/my-trips');
    } catch (error) {
      console.error('Error creating request:', error);
    } finally {
      setSubmitting(false);
    }
  };

  const handleOpenChat = async () => {
    if (!trip || chatLoading) return;
    setChatLoading(true);
    try {
      const response = await api.getOrCreateConversation(trip.id, user!.id);
      navigate(`/messages/${response.data.id}`);
    } catch (error) {
      console.error('Error opening chat:', error);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div style={{ fontSize: '48px', marginBottom: '16px' }}></div>
        Загрузка...
      </div>
    );
  }
  
  if (!trip) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '60px' }}>
        <div style={{ fontSize: '64px', marginBottom: '16px' }}></div>
        <h3>Поездка не найдена</h3>
        <Link to="/" className="btn btn-primary" style={{ marginTop: '20px' }}>
          На главную
        </Link>
      </div>
    );
  }

  const isOwner = user?.id === trip.driver_id;

  return (
    <div className="trip-details-page">
      <Link to="/" style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginBottom: '24px', color: '#6b7280' }}>
        ← Назад к поиску
      </Link>
      
      <div className="card" style={{ marginBottom: '24px' }}>
        {/* Header */}
        <div className="trip-header">
          <h1>{trip.from_city} → {trip.to_city}</h1>
          <div className="trip-meta">
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', marginRight: '16px' }}>
              {trip.departure_date}
            </span>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '8px' }}>
              {trip.departure_time}
            </span>
          </div>
        </div>

        {/* Price & Seats */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          padding: '24px',
          background: 'linear-gradient(135deg, #00a8e8 0%, #007ea7 100%)',
          borderRadius: '16px',
          color: 'white',
          marginBottom: '24px'
        }}>
          <div>
            <div style={{ fontSize: '14px', opacity: 0.9 }}>Цена за место</div>
            <div style={{ fontSize: '36px', fontWeight: 800 }}>{trip.price_per_seat} ₽</div>
          </div>
          <div style={{ textAlign: 'right' }}>
            <div style={{ fontSize: '14px', opacity: 0.9 }}>Доступно мест</div>
            <div style={{ fontSize: '36px', fontWeight: 800 }}>
              {trip.available_seats > 0 ? `✅ ${trip.available_seats}` : '❌ 0'}
            </div>
          </div>
        </div>

        {/* Driver */}
        <div className="trip-driver">
          <div className="driver-avatar">
            {trip.driver.name.charAt(0).toUpperCase()}
          </div>
          <div className="driver-info">
            <h3>{trip.driver.name}</h3>
            {trip.driver.rating && (
              <p style={{ color: '#faad14', display: 'flex', alignItems: 'center', gap: '4px' }}>
                {trip.driver.rating}
              </p>
            )}
            {trip.driver.phone && <p> {trip.driver.phone}</p>}
          </div>
        </div>

        {/* Description */}
        {trip.description && (
          <div style={{ marginBottom: '24px' }}>
            <h3 style={{ marginBottom: '12px', color: '#1a1a2e' }}>Описание</h3>
            <p style={{ color: '#6b7280', lineHeight: 1.7 }}>{trip.description}</p>
          </div>
        )}

        {/* Actions */}
        {isOwner ? (
          <div style={{ 
            padding: '16px', 
            background: '#f3f4f6', 
            borderRadius: '12px',
            textAlign: 'center',
            color: '#6b7280'
          }}>
            Это ваша поездка
          </div>
        ) : !isAuthenticated ? (
          <Link 
            to={`/login?redirect=/trips/${trip.id}`} 
            className="btn btn-secondary"
            style={{ width: '100%' }}
          >
            Войдите, чтобы отправить заявку
          </Link>
        ) : trip.available_seats > 0 ? (
          <>
            <button 
              onClick={() => setShowModal(true)} 
              className="btn btn-primary"
              style={{ width: '100%', padding: '16px' }}
            >
              Забронировать место
            </button>
            <button 
              onClick={handleOpenChat}
              disabled={chatLoading}
              className="btn btn-secondary"
              style={{ width: '100%', marginTop: '12px' }}
            >
              {chatLoading ? 'Загрузка...' : 'Написать водителю'}
            </button>
          </>
        ) : (
          <div style={{ 
            padding: '16px', 
            background: '#fff2f0', 
            borderRadius: '12px',
            textAlign: 'center',
            color: '#cf1322'
          }}>
            Нет доступных мест
          </div>
        )}
      </div>

      {/* Booking Modal */}
      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>Заявка на поездку</h2>
            <div className="form-group">
              <label>Количество мест:</label>
              <select 
                value={seats} 
                onChange={(e) => setSeats(Number(e.target.value))}
                style={{ width: '100%', padding: '14px 16px', borderRadius: '12px', border: '2px solid #e5e7eb' }}
              >
                {[1, 2, 3, 4].filter(s => s <= trip.available_seats).map(s => (
                  <option key={s} value={s}>{s}</option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label>Сообщение водителю:</label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="Необязательно"
                rows={3}
                style={{ width: '100%', padding: '14px 16px', borderRadius: '12px', border: '2px solid #e5e7eb', resize: 'vertical' }}
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowModal(false)} className="btn btn-secondary">
                Отмена
              </button>
              <button onClick={handleRequest} disabled={submitting} className="btn btn-primary">
                {submitting ? 'Отправка...' : 'Отправить заявку'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
