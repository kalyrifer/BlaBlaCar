import { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix Leaflet default marker icon issue
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

// Russian cities as predefined options
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

// Custom red icon for destination
const destinationIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

// Component to handle map click events
function MapClickHandler({ onSelect }: { onSelect: (lat: number, lng: number) => void }) {
  useMapEvents({
    click: (e) => {
      onSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

// Component to center map on a specific location
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
  
  // Map center - default to Moscow
  const center: [number, number] = [55.7558, 37.6173];
  
  // Find coordinates from city name
  const findCityCoords = (cityName: string): [number, number] | null => {
    const city = RUSSIAN_CITIES.find(c => 
      c.name.toLowerCase() === cityName.toLowerCase()
    );
    return city ? [city.lat, city.lng] : null;
  };
  
  // Reverse geocoding - get city name from coordinates using OpenStreetMap Nominatim
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
  
  // Filter cities for dropdown
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
  
  return (
    <div className="map-container">
      {/* City selection dropdowns */}
      <div className="map-controls">
        <div className="city-select-wrapper">
          <label className="city-label">📍 Откуда</label>
          <div className="city-input-wrapper">
            <input
              type="text"
              placeholder="Выберите город"
              value={searchFrom || fromCity || ''}
              onChange={(e) => {
                setSearchFrom(e.target.value);
                setShowFromDropdown(true);
              }}
              onFocus={() => setShowFromDropdown(true)}
              className="city-input"
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
        </div>
        
        <div className="city-select-wrapper">
          <label className="city-label">🏁 Куда</label>
          <div className="city-input-wrapper">
            <input
              type="text"
              placeholder="Выберите город"
              value={searchTo || toCity || ''}
              onChange={(e) => {
                setSearchTo(e.target.value);
                setShowToDropdown(true);
              }}
              onFocus={() => setShowToDropdown(true)}
              className="city-input"
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
      </div>
      
      {/* Instructions */}
      <div className="map-instructions">
        Нажмите на карту чтобы выбрать точку отправления или прибытия
      </div>
      
      {/* Leaflet Map */}
      <MapContainer
        center={center}
        zoom={4}
        style={{ height: '400px', width: '100%', borderRadius: '12px' }}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* From location marker (green) */}
        {fromCoords && (
          <Marker 
            position={fromCoords} 
            icon={new L.Icon({
              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowSize: [41, 41]
            })}
          />
        )}
        
        {/* To location marker (red) */}
        {toCoords && <Marker position={toCoords} icon={destinationIcon} />}
        
        {/* Click handler */}
        <MapClickHandler onSelect={(lat, lng) => {
          if (!fromCoords) {
            handleFromClick(lat, lng);
          } else if (!toCoords) {
            handleToClick(lat, lng);
          } else {
            // Reset and start over
            setFromCoords(null);
            setToCoords(null);
            handleFromClick(lat, lng);
          }
        }} />
        
        {/* Center on from location */}
        {fromCoords && <MapCenter lat={fromCoords[0]} lng={fromCoords[1]} />}
      </MapContainer>
      
      {/* Selected route display */}
      {(fromCoords || toCoords) && (
        <div className="selected-route">
          {fromCoords && toCoords && (
            <div className="route-line">
              <span className="route-from">📍 Откуда: выбрано</span>
              <span className="route-arrow">→</span>
              <span className="route-to">🏁 Куда: выбрано</span>
            </div>
          )}
          <button 
            className="clear-btn"
            onClick={() => {
              setFromCoords(null);
              setToCoords(null);
            }}
          >
            Очистить
          </button>
        </div>
      )}
      
      <style>{`
        .map-container {
          width: 100%;
        }
        
        .map-controls {
          display: flex;
          gap: 16px;
          margin-bottom: 16px;
          flex-wrap: wrap;
        }
        
        .city-select-wrapper {
          flex: 1;
          min-width: 200px;
          position: relative;
        }
        
        .city-label {
          display: block;
          font-weight: 600;
          margin-bottom: 8px;
          color: #333;
        }
        
        .city-input-wrapper {
          position: relative;
        }
        
        .city-input {
          width: 100%;
          padding: 12px 16px;
          border: 2px solid #e5e7eb;
          border-radius: 8px;
          font-size: 16px;
          transition: border-color 0.2s;
        }
        
        .city-input:focus {
          outline: none;
          border-color: #3b82f6;
        }
        
        .city-dropdown {
          position: absolute;
          top: 100%;
          left: 0;
          right: 0;
          background: white;
          border: 1px solid #e5e7eb;
          border-radius: 8px;
          box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
          max-height: 200px;
          overflow-y: auto;
          z-index: 1000;
        }
        
        .city-option {
          padding: 12px 16px;
          cursor: pointer;
          transition: background-color 0.2s;
        }
        
        .city-option:hover {
          background-color: #f3f4f6;
        }
        
        .map-instructions {
          text-align: center;
          color: #6b7280;
          margin-bottom: 12px;
          font-size: 14px;
        }
        
        .selected-route {
          display: flex;
          align-items: center;
          justify-content: space-between;
          margin-top: 16px;
          padding: 16px;
          background: #f3f4f6;
          border-radius: 8px;
        }
        
        .route-line {
          display: flex;
          align-items: center;
          gap: 12px;
        }
        
        .route-arrow {
          color: #6b7280;
          font-size: 20px;
        }
        
        .clear-btn {
          padding: 8px 16px;
          background: #ef4444;
          color: white;
          border: none;
          border-radius: 6px;
          cursor: pointer;
          font-size: 14px;
          transition: background-color 0.2s;
        }
        
        .clear-btn:hover {
          background: #dc2626;
        }
      `}</style>
    </div>
  );
}
