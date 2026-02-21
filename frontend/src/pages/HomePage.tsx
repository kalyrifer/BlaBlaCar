import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();
  const [searchData, setSearchData] = useState({
    from_city: '',
    to_city: '',
    date: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (searchData.from_city) params.set('from_city', searchData.from_city);
    if (searchData.to_city) params.set('to_city', searchData.to_city);
    if (searchData.date) params.set('date', searchData.date);
    navigate(`/trips?${params.toString()}`);
  };

  return (
    <div className="home-page">
      {/* Hero Section */}
      <div style={{ 
        background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
        padding: '60px 20px',
        borderRadius: '24px',
        marginBottom: '40px',
        textAlign: 'center',
        color: 'white',
        position: 'relative',
        overflow: 'hidden'
      }}>
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'0.05\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
        }}></div>
        <div style={{ position: 'relative', zIndex: 1 }}>
          <h1 style={{ 
            fontSize: '48px', 
            fontWeight: 800, 
            marginBottom: '16px',
            background: 'linear-gradient(135deg, #00a8e8 0%, #00d4ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            Найди попутчика
          </h1>
          <p style={{ 
            fontSize: '20px', 
            opacity: 0.9,
            maxWidth: '500px',
            margin: '0 auto'
          }}>
            Путешествуй с комфортом по выгодным ценам
          </p>
        </div>
      </div>

      {/* Search Form */}
      <div className="search-form">
        <h2>Куда ты едешь?</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-row-3">
            <div className="form-group">
              <label>📍 Откуда</label>
              <input
                type="text"
                placeholder="Город отправления"
                value={searchData.from_city}
                onChange={(e) => setSearchData({ ...searchData, from_city: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>🏁 Куда</label>
              <input
                type="text"
                placeholder="Город прибытия"
                value={searchData.to_city}
                onChange={(e) => setSearchData({ ...searchData, to_city: e.target.value })}
                required
              />
            </div>
            <div className="form-group">
              <label>📅 Дата</label>
              <input
                type="date"
                value={searchData.date}
                onChange={(e) => setSearchData({ ...searchData, date: e.target.value })}
              />
            </div>
          </div>
          <button type="submit" className="btn btn-primary btn-lg">
            🔍 Найти поездку
          </button>
        </form>
      </div>

      {/* Features */}
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
        gap: '24px',
        marginTop: '40px'
      }}>
        <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '16px',
            background: 'linear-gradient(135deg, #00a8e8 0%, #00d4ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            💰
          </div>
          <h3 style={{ marginBottom: '8px', color: '#1a1a2e' }}>Экономия</h3>
          <p style={{ color: '#6b7280' }}>
            Путешествуй дешевле, чем на такси или автобусе
          </p>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '16px',
            background: 'linear-gradient(135deg, #00a8e8 0%, #00d4ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            🚗
          </div>
          <h3 style={{ marginBottom: '8px', color: '#1a1a2e' }}>Комфорт</h3>
          <p style={{ color: '#6b7280' }}>
            Выбирай удобное время и маршрут
          </p>
        </div>
        <div className="card" style={{ textAlign: 'center', padding: '32px' }}>
          <div style={{ 
            fontSize: '48px', 
            marginBottom: '16px',
            background: 'linear-gradient(135deg, #00a8e8 0%, #00d4ff 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}>
            👥
          </div>
          <h3 style={{ marginBottom: '8px', color: '#1a1a2e' }}>Общение</h3>
          <p style={{ color: '#6b7280' }}>
            Познакомься с интересными людьми
          </p>
        </div>
      </div>
    </div>
  );
}
