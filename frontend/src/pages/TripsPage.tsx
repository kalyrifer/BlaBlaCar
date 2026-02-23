import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { tripsApi } from '../services/api';
import type { Trip } from '../types';

export default function TripsPage() {
  const [searchParams] = useSearchParams();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrips = async () => {
      setLoading(true);
      try {
        const fromCity = searchParams.get('from_city') || '';
        const toCity = searchParams.get('to_city') || '';
        const date = searchParams.get('date') || undefined;
        
        const response = await tripsApi.search({ from_city: fromCity, to_city: toCity, date });
        setTrips(response.data.items);
      } catch (error) {
        console.error('Error fetching trips:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrips();
  }, [searchParams]);

  if (loading) {
    return (
      <div className="loading">
        <div style={{ fontSize: '48px', marginBottom: '16px' }}></div>
        Поиск поездок...
      </div>
    );
  }

  return (
    <div className="trips-page">
      <h1 className="page-title">
        Найденные поездки
        {searchParams.get('from_city') && searchParams.get('to_city') && (
          <span style={{ 
            display: 'block', 
            fontSize: '18px', 
            fontWeight: 400, 
            color: '#6b7280',
            marginTop: '8px'
          }}>
            {searchParams.get('from_city')} → {searchParams.get('to_city')}
            {searchParams.get('date') && ` • ${searchParams.get('date')}`}
          </span>
        )}
      </h1>
      
      {trips.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}></div>
          <h3 style={{ marginBottom: '8px', color: '#1a1a2e' }}>Поездок не найдено</h3>
          <p style={{ color: '#6b7280', marginBottom: '24px' }}>
            Попробуйте изменить параметры поиска или поискать на другую дату
          </p>
          <Link to="/" className="btn btn-primary">
            Изменить поиск
          </Link>
        </div>
      ) : (
        <div className="trips-list">
          {trips.map((trip) => (
            <Link 
              to={`/trips/${trip.id}`} 
              key={trip.id} 
              className="trip-card"
              style={{ textDecoration: 'none' }}
            >
              <div className="trip-info">
                <div className="trip-route">
                  <span className="city">{trip.from_city}</span>
                  <span className="arrow">→</span>
                  <span className="city">{trip.to_city}</span>
                </div>
                <div className="trip-details">
                  <span>{trip.departure_date}</span>
                  <span>{trip.departure_time}</span>
                  <span>{trip.driver.name}</span>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <div className="trip-price">{trip.price_per_seat} ₽</div>
                <div style={{ 
                  color: trip.available_seats > 0 ? '#52c41a' : '#ff4d4f',
                  fontSize: '14px',
                  fontWeight: 600,
                  marginTop: '4px'
                }}>
                  {trip.available_seats > 0 ? `✅ ${trip.available_seats} мест` : '❌ Нет мест'}
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
