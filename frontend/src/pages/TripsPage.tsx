import { useEffect, useState, useCallback } from 'react';
import { useSearchParams, Link, useNavigate } from 'react-router-dom';
import { tripsApi } from '../services/api';
import type { Trip } from '../types';
import Map from '../components/Map';

export default function TripsPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const [trips, setTrips] = useState<Trip[]>([]);
  const [loading, setLoading] = useState(true);
  const [showMap, setShowMap] = useState(true);
  
  // Local state for input fields - separate from URL params
  const [fromInput, setFromInput] = useState('');
  const [toInput, setToInput] = useState('');

  // Get current search values from URL
  const fromCity = searchParams.get('from_city') || '';
  const toCity = searchParams.get('to_city') || '';
  const date = searchParams.get('date') || '';

  // Sync local state with URL params on initial load
  useEffect(() => {
    setFromInput(fromCity);
    setToInput(toCity);
  }, []);

  // Fetch trips only when URL params change (not on every keystroke)
  useEffect(() => {
    const fetchTrips = async () => {
      setLoading(true);
      try {
        const response = await tripsApi.search({ 
          from_city: fromCity, 
          to_city: toCity, 
          date: date || undefined 
        });
        setTrips(response.data.items);
      } catch (error) {
        console.error('Error fetching trips:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTrips();
  }, [fromCity, toCity, date]);

  const handleFromSelect = (lat: number, lng: number, cityName: string) => {
    setFromInput(cityName);
  };

  const handleToSelect = (lat: number, lng: number, cityName: string) => {
    setToInput(cityName);
  };

  const handleSearch = () => {
    // Update URL params only when clicking the search button
    const params = new URLSearchParams();
    if (fromInput) params.set('from_city', fromInput);
    if (toInput) params.set('to_city', toInput);
    if (date) params.set('date', date);
    navigate(`/trips?${params.toString()}`);
  };

  const handleFromCityChange = (value: string) => {
    setFromInput(value);
  };

  const handleToCityChange = (value: string) => {
    setToInput(value);
  };

  const handleDateChange = (value: string) => {
    const params = new URLSearchParams(searchParams);
    if (value) {
      params.set('date', value);
    } else {
      params.delete('date');
    }
    setSearchParams(params);
  };

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
        Поиск поездок
        {fromCity && toCity && (
          <span style={{ 
            display: 'block', 
            fontSize: '18px', 
            fontWeight: 400, 
            color: '#6b7280',
            marginTop: '8px'
          }}>
            {fromCity} → {toCity}
            {date && ` • ${date}`}
          </span>
        )}
      </h1>

      {/* Map for selecting destinations */}
      <div className="search-section" style={{ marginBottom: '32px' }}>
        <div className="search-inputs" style={{ 
          display: 'flex', 
          gap: '12px', 
          marginBottom: '16px',
          flexWrap: 'wrap'
        }}>
          <input
            type="text"
            placeholder="Откуда"
            value={fromInput}
            onChange={(e) => handleFromCityChange(e.target.value)}
            className="search-input"
            style={{ flex: 1, minWidth: '150px' }}
          />
          <input
            type="text"
            placeholder="Куда"
            value={toInput}
            onChange={(e) => handleToCityChange(e.target.value)}
            className="search-input"
            style={{ flex: 1, minWidth: '150px' }}
          />
          <input
            type="date"
            value={date}
            onChange={(e) => handleDateChange(e.target.value)}
            className="search-input"
            style={{ flex: 1, minWidth: '150px' }}
          />
          <button 
            onClick={() => setShowMap(!showMap)}
            className="btn btn-secondary"
            style={{ padding: '12px 20px' }}
          >
            {showMap ? 'Скрыть карту' : 'Показать карту'}
          </button>
          <button 
            onClick={handleSearch}
            className="btn btn-primary"
            style={{ padding: '12px 20px' }}
          >
            Найти
          </button>
        </div>

        {/* Interactive Map */}
        {showMap && (
          <div className="map-wrapper" style={{ marginTop: '20px' }}>
            <Map 
              fromCity={fromInput}
              toCity={toInput}
              onFromSelect={handleFromSelect}
              onToSelect={handleToSelect}
            />
          </div>
        )}
      </div>

      {/* Results */}
      <div className="trips-results">
        {trips.length === 0 ? (
          <div className="card" style={{ textAlign: 'center', padding: '60px 20px' }}>
            <div style={{ fontSize: '64px', marginBottom: '16px' }}></div>
            <h3 style={{ marginBottom: '8px', color: '#1a1a2e' }}>
              {fromCity || toCity ? 'Поездок не найдено' : 'Выберите маршрут'}
            </h3>
            <p style={{ color: '#6b7280', marginBottom: '24px' }}>
              {fromCity || toCity 
                ? 'Попробуйте изменить параметры поиска или поискать на другую дату'
                : 'Используйте карту выше или введите города в поля выше'
              }
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

      <style>{`
        .search-input {
          padding: 12px 16px;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 16px;
          transition: border-color 0.2s;
        }
        
        .search-input:focus {
          outline: none;
          border-color: #3b82f6;
        }
        
        .map-wrapper {
          border-radius: 12px;
          overflow: hidden;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        
        .trips-results {
          margin-top: 24px;
        }
      `}</style>
    </div>
  );
}
