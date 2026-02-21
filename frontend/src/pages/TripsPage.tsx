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
    return <div>Загрузка...</div>;
  }

  return (
    <div className="trips-page">
      <h1>Найденные поездки</h1>
      
      {trips.length === 0 ? (
        <p>Поездок не найдено</p>
      ) : (
        <div className="trips-list">
          {trips.map((trip) => (
            <Link to={`/trips/${trip.id}`} key={trip.id} className="trip-card">
              <div className="trip-driver">
                <span className="driver-name">{trip.driver.name}</span>
                {trip.driver.rating && <span className="rating">★ {trip.driver.rating}</span>}
              </div>
              <div className="trip-route">
                {trip.from_city} → {trip.to_city}
              </div>
              <div className="trip-info">
                <span>{trip.departure_date}, {trip.departure_time}</span>
                <span>{trip.available_seats} места · {trip.price_per_seat} ₽</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
