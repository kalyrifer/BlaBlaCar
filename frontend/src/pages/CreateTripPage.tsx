import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { tripsApi } from '../services/api';

export default function CreateTripPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    from_city: '',
    to_city: '',
    departure_date: '',
    departure_time: '',
    available_seats: 1,
    price_per_seat: 0,
    description: '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await tripsApi.create(formData);
      navigate('/my-trips');
    } catch (error) {
      console.error('Error creating trip:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-trip-page">
      <h1>Создать поездку</h1>
      
      <form onSubmit={handleSubmit} className="create-trip-form">
        <div className="form-group">
          <label>Откуда</label>
          <input
            type="text"
            value={formData.from_city}
            onChange={(e) => setFormData({ ...formData, from_city: e.target.value })}
            required
          />
        </div>

        <div className="form-group">
          <label>Куда</label>
          <input
            type="text"
            value={formData.to_city}
            onChange={(e) => setFormData({ ...formData, to_city: e.target.value })}
            required
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Дата</label>
            <input
              type="date"
              value={formData.departure_date}
              onChange={(e) => setFormData({ ...formData, departure_date: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>Время</label>
            <input
              type="time"
              value={formData.departure_time}
              onChange={(e) => setFormData({ ...formData, departure_time: e.target.value })}
              required
            />
          </div>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Мест</label>
            <input
              type="number"
              min="1"
              max="8"
              value={formData.available_seats}
              onChange={(e) => setFormData({ ...formData, available_seats: Number(e.target.value) })}
              required
            />
          </div>

          <div className="form-group">
            <label>Цена за место (₽)</label>
            <input
              type="number"
              min="0"
              value={formData.price_per_seat}
              onChange={(e) => setFormData({ ...formData, price_per_seat: Number(e.target.value) })}
              required
            />
          </div>
        </div>

        <div className="form-group">
          <label>Описание</label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Дополнительная информация о поездке"
          />
        </div>

        <div className="form-actions">
          <button type="button" onClick={() => navigate(-1)} className="btn btn-secondary">
            Отмена
          </button>
          <button type="submit" disabled={loading} className="btn btn-primary">
            {loading ? 'Создание...' : 'Создать поездку'}
          </button>
        </div>
      </form>
    </div>
  );
}
