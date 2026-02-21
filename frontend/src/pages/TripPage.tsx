import { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { tripsApi } from '../services/api';
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

  if (loading) return <div>Загрузка...</div>;
  if (!trip) return <div>Поездка не найдена</div>;

  const isOwner = user?.id === trip.driver_id;

  return (
    <div className="trip-page">
      <Link to="/">&larr; Назад к поиску</Link>
      
      <div className="trip-details">
        <h1>{trip.from_city} → {trip.to_city}</h1>
        
        <div className="trip-info">
          <p><strong>Дата:</strong> {trip.departure_date}, {trip.departure_time}</p>
          <p><strong>Цена:</strong> {trip.price_per_seat} ₽ за место</p>
          <p><strong>Мест:</strong> {trip.available_seats}</p>
          {trip.description && <p><strong>Описание:</strong> {trip.description}</p>}
        </div>

        <div className="driver-info">
          <h3>Водитель</h3>
          <p>{trip.driver.name}</p>
          {trip.driver.rating && <p>Рейтинг: ★ {trip.driver.rating}</p>}
          {trip.driver.phone && <p>Телефон: {trip.driver.phone}</p>}
        </div>

        {!isOwner && isAuthenticated && (
          <button onClick={() => setShowModal(true)} className="btn btn-primary">
            Отправить заявку
          </button>
        )}

        {!isAuthenticated && (
          <Link to={`/login?redirect=/trips/${trip.id}`} className="btn btn-secondary">
            Войдите, чтобы отправить заявку
          </Link>
        )}
      </div>

      {showModal && (
        <div className="modal">
          <div className="modal-content">
            <h2>Заявка на поездку</h2>
            <div className="form-group">
              <label>Количество мест:</label>
              <select value={seats} onChange={(e) => setSeats(Number(e.target.value))}>
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
              />
            </div>
            <div className="modal-actions">
              <button onClick={() => setShowModal(false)} className="btn btn-secondary">Отмена</button>
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
