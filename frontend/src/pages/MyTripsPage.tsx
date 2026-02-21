import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { tripsApi } from '../services/api';
import type { Trip } from '../types';

export default function MyTripsPage() {
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const response = await tripsApi.getMyTrips();
        setTrips(response.data.items);
      } catch (error) {
        console.error('Error fetching trips:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrips();
  }, []);

  if (loading) return <div>Загрузка...</div>;

  return (
    <div className="my-trips-page">
      <h1>Мои поездки</h1>
      
      <div className="tabs">
        <div className="tab active">Как водитель</div>
      </div>

      {trips.length === 0 ? (
        <p>У вас пока нет поездок</p>
      ) : (
        <div className="trips-list">
          {trips.map((trip) => (
            <Link to={`/trips/${trip.id}`} key={trip.id} className="trip-card">
              <div className="trip-route">
                {trip.from_city} → {trip.to_city}
              </div>
              <div className="trip-info">
                <span>{trip.departure_date}, {trip.departure_time}</span>
                <span className={`status status-${trip.status}`}>{trip.status}</span>
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
