import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
});

interface MapProps {
  fromCity?: string;
  toCity?: string;
  onFromSelect?: (lat: number, lng: number, cityName: string) => void;
  onToSelect?: (lat: number, lng: number, cityName: string) => void;
}

const RUSSIAN_CITIES = [
  { name: 'Москва', lat: 55.7558, lng: 37.6173 },
  { name: 'Санкт-Петербург', lat: 59.9311, lng: 30.3609 },
  { name: 'Новосибирск', lat: 55.0084, lng: 82.9357 },
  { name: 'Екатеринбург', lat: 56.8389, lng: 60.6057 },
  { name: 'Казань', lat: 55.8304, lng: 49.0661 },
  { name: 'Нижний Новгород', lat: 56.296, lng: 43.9368 },
  { name: 'Челябинск', lat: 55.1644, lng: 61.4368 },
  { name: 'Самара', lat: 53.1955, lng: 50.1018 },
  { name: 'Омск', lat: 54.9893, lng: 73.3682 },
  { name: 'Ростов-на-Дону', lat: 47.2221, lng: 39.7203 },
  { name: 'Уфа', lat: 54.7351, lng: 55.9837 },
  { name: 'Воронеж', lat: 51.6708, lng: 39.2153 },
  { name: 'Волгоград', lat: 48.7071, lng: 44.5169 },
  { name: 'Красноярск', lat: 56.0153, lng: 92.8938 },
  { name: 'Пермь', lat: 58.0105, lng: 56.2292 },
  { name: 'Тюмень', lat: 57.153, lng: 65.5343 },
  { name: 'Саратов', lat: 51.5331, lng: 46.0343 },
  { name: 'Тольятти', lat: 53.5187, lng: 49.3894 },
  { name: 'Ижевск', lat: 56.8527, lng: 53.2061 },
  { name: 'Кемерово', lat: 55.3406, lng: 86.0743 },
  { name: 'Барнаул', lat: 53.3548, lng: 83.7696 },
  { name: 'Иркутск', lat: 52.2868, lng: 104.2344 },
  { name: 'Ульяновск', lat: 54.3165, lng: 48.3837 },
  { name: 'Хабаровск', lat: 48.4805, lng: 135.0716 },
  { name: 'Ярославль', lat: 57.6260, lng: 39.8935 },
  { name: 'Владивосток', lat: 43.1332, lng: 131.9113 },
  { name: 'Махачкала', lat: 42.9830, lng: 47.5029 },
  { name: 'Томск', lat: 56.4949, lng: 84.9746 },
  { name: 'Оренбург', lat: 51.7681, lng: 55.0975 },
  { name: 'Краснодар', lat: 45.0355, lng: 38.9753 },
];

// Minimal dark circle markers
const createMinimalIcon = (type: 'from' | 'to') => {
  const color = type === 'from' ? '#2563eb' : '#dc2626';
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="28" height="28">
      <circle cx="12" cy="12" r="10" fill="${color}" stroke="white" stroke-width="2"/>
      <circle cx="12" cy="12" r="4" fill="white"/>
    </svg>
  `;
  return new L.Icon({
    iconUrl: `data:image/svg+xml;base64,${btoa(svg)}`,
    iconSize: [28, 28],
    iconAnchor: [14, 14],
  });
};

function MapClickHandler({ onSelect }: { onSelect: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      onSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

function MapCenter({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  
  useEffect(() => {
    if (lat && lng) {
      map.setView([lat, lng], map.getZoom());
    }
  }, [lat, lng, map]);
  
  return null;
}

export default function Map({
  fromCity,
  toCity,
  onFromSelect,
  onToSelect
}: MapProps) {
  const [fromCoords, setFromCoords] = useState<[number, number] | null>(null);
  const [toCoords, setToCoords] = useState<[number, number] | null>(null);
  const [showFromDropdown, setShowFromDropdown] = useState(false);
  const [showToDropdown, setShowToDropdown] = useState(false);
  const [searchFrom, setSearchFrom] = useState('');
  const [searchTo, setSearchTo] = useState('');
  
  const center: [number, number] = [55.7558, 37.6173];
  
  const findCityCoords = (cityName: string): [number, number] | null => {
    const city = RUSSIAN_CITIES.find(c => 
      c.name.toLowerCase() === cityName.toLowerCase()
    );
    return city ? [city.lat, city.lng] : null;
  };
  
  const getCityFromCoords = async (lat: number, lng: number): Promise<string> => {
    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&addressdetails=1&language=ru`
      );
      const data = await response.json();
      return data.address.city || data.address.town || data.address.village || data.address.county || 'Unknown';
    } catch (error) {
      console.error('Error reverse geocoding:', error);
      return 'Unknown';
    }
  };
  
  const handleFromClick = async (lat: number, lng: number) => {
    const cityName = await getCityFromCoords(lat, lng);
    setFromCoords([lat, lng]);
    setShowFromDropdown(false);
    setSearchFrom('');
    if (onFromSelect) {
      onFromSelect(lat, lng, cityName);
    }
  };
  
  const handleToClick = async (lat: number, lng: number) => {
    const cityName = await getCityFromCoords(lat, lng);
    setToCoords([lat, lng]);
    setShowToDropdown(false);
    setSearchTo('');
    if (onToSelect) {
      onToSelect(lat, lng, cityName);
    }
  };
  
  const filteredFromCities = RUSSIAN_CITIES.filter(city =>
    city.name.toLowerCase().includes(searchFrom.toLowerCase())
  );
  
  const filteredToCities = RUSSIAN_CITIES.filter(city =>
    city.name.toLowerCase().includes(searchTo.toLowerCase())
  );
  
  const handleFromCitySelect = (city: typeof RUSSIAN_CITIES[0]) => {
    setFromCoords([city.lat, city.lng]);
    setShowFromDropdown(false);
    setSearchFrom('');
    if (onFromSelect) {
      onFromSelect(city.lat, city.lng, city.name);
    }
  };
  
  const handleToCitySelect = (city: typeof RUSSIAN_CITIES[0]) => {
    setToCoords([city.lat, city.lng]);
    setShowToDropdown(false);
    setSearchTo('');
    if (onToSelect) {
      onToSelect(city.lat, city.lng, city.name);
    }
  };

  const handleMapClick = (lat: number, lng: number) => {
    if (!fromCoords) {
      handleFromClick(lat, lng);
    } else if (!toCoords) {
      handleToClick(lat, lng);
    } else {
      setFromCoords(null);
      setToCoords(null);
      handleFromClick(lat, lng);
    }
  };
  
  return (
    <div className="map-container">
      {/* Minimal Search Bar */}
      <div className="map-search">
        <div className="search-field">
          <span className="search-dot from"></span>
          <input
            type="text"
            placeholder="Откуда"
            value={searchFrom || fromCity || ''}
            onChange={(e) => {
              setSearchFrom(e.target.value);
              setShowFromDropdown(true);
            }}
            onFocus={() => setShowFromDropdown(true)}
            className="search-input"
          />
          {showFromDropdown && filteredFromCities.length > 0 && (
            <div className="city-dropdown">
              {filteredFromCities.map((city) => (
                <div
                  key={city.name}
                  className="city-option"
                  onClick={() => handleFromCitySelect(city)}
                >
                  {city.name}
                </div>
              ))}
            </div>
          )}
        </div>
        
        <div className="search-divider"></div>
        
        <div className="search-field">
          <span className="search-dot to"></span>
          <input
            type="text"
            placeholder="Куда"
            value={searchTo || toCity || ''}
            onChange={(e) => {
              setSearchTo(e.target.value);
              setShowToDropdown(true);
            }}
            onFocus={() => setShowToDropdown(true)}
            className="search-input"
          />
          {showToDropdown && filteredToCities.length > 0 && (
            <div className="city-dropdown">
              {filteredToCities.map((city) => (
                <div
                  key={city.name}
                  className="city-option"
                  onClick={() => handleToCitySelect(city)}
                >
                  {city.name}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
      
      {/* Leaflet Map - Clean Style */}
      <MapContainer
        center={center}
        zoom={4}
        style={{ height: '350px', width: '100%', borderRadius: '8px' }}
        zoomControl={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {fromCoords && (
          <Marker position={fromCoords} icon={createMinimalIcon('from')} />
        )}
        
        {toCoords && (
          <Marker position={toCoords} icon={createMinimalIcon('to')} />
        )}
        
        <MapClickHandler onSelect={handleMapClick} />
        
        {fromCoords && <MapCenter lat={fromCoords[0]} lng={fromCoords[1]} />}
      </MapContainer>
      
      {/* Minimal route info */}
      {(fromCoords || toCoords) && (
        <div className="route-info">
          <div className="route-points">
            <span className="route-point from">
              <span className="point-dot"></span>
              {fromCoords ? 'Точка отправления' : 'Выберите'}
            </span>
            <span className="route-line-h"></span>
            <span className="route-point to">
              <span className="point-dot"></span>
              {toCoords ? 'Пункт назначения' : 'Выберите'}
            </span>
          </div>
          <button 
            className="clear-btn"
            onClick={() => {
              setFromCoords(null);
              setToCoords(null);
            }}
          >
            Сбросить
          </button>
        </div>
      )}
      
      <style>{`
        .map-container {
          width: 100%;
        }
        
        .map-search {
          display: flex;
          align-items: center;
          background: #ffffff;
          border: 1px solid #d1d5db;
          border-radius: 8px;
          padding: 4px;
          margin-bottom: 12px;
        }
        
        .search-field {
          flex: 1;
          position: relative;
          display: flex;
          align-items: center;
        }
        
        .search-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          margin: 0 12px;
          flex-shrink: 0;
        }
        
        .search-dot.from {
          background: #2563eb;
        }
        
        .search-dot.to {
          background: #dc2626;
        }
        
        .search-divider {
          width: 1px;
          height: 24px;
          background: #e5e5e5;
          margin: 0 4px;
        }
        
        .search-input {
          flex: 1;
          border: none;
          background: transparent;
          padding: 10px 8px 10px 0;
          font-size: 14px;
          font-weight: 400;
          color: #333;
          outline: none;
        }
        
        .search-input::placeholder {
          color: #999;
        }
        
        .city-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 1px solid #e5e5e5;
          border-radius: 6px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.08);
          max-height: 180px;
          overflow-y: auto;
          z-index: 1000;
          margin-top: 4px;
        }
        
        .city-option {
          padding: 10px 14px;
          font-size: 13px;
          color: #333;
          cursor: pointer;
          transition: background 0.15s;
        }
        
        .city-option:hover {
          background: #f5f5f5;
        }
        
        .route-info {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 12px;
          padding: 12px 16px;
          background: #ffffff;
          border: 1px solid #d1d5db;
          border-radius: 6px;
        }
        
        .route-points {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .route-point {
          display: flex;
          align-items: center;
          gap: 6px;
          font-size: 12px;
          color: #374151;
        }
        
        .point-dot {
          width: 6px;
          height: 6px;
          border-radius: 50%;
        }
        
        .route-point.from .point-dot {
          background: #2563eb;
        }
        
        .route-point.to .point-dot {
          background: #dc2626;
        }
        
        .route-line-h {
          width: 20px;
          height: 1px;
          background: #ddd;
        }
        
        .clear-btn {
          padding: 6px 12px;
          background: #f3f4f6;
          color: #374151;
          border: 1px solid #d1d5db;
          border-radius: 4px;
          cursor: pointer;
          font-size: 12px;
          transition: all 0.15s;
        }
        
        .clear-btn:hover {
          background: #e5e7eb;
          color: #111;
        }
        
        /* Leaflet overrides */
        .leaflet-container {
          font-family: inherit;
        }
        
        .leaflet-control-zoom {
          border: none !important;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        }
        
        .leaflet-control-zoom a {
          background: white !important;
          color: #333 !important;
        }
      `}</style>
    </div>
  );
}
