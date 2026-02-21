import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function HomePage() {
  const navigate = useNavigate();
  const [fromCity, setFromCity] = useState('');
  const [toCity, setToCity] = useState('');
  const [date, setDate] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    params.set('from_city', fromCity);
    params.set('to_city', toCity);
    if (date) params.set('date', date);
    navigate(`/trips?${params.toString()}`);
  };

  return (
    <div className="home-page">
      <section className="hero">
        <h1>Найдите попутчика</h1>
        <p>Путешествуйте с комфортом по доступным ценам</p>
      </section>

      <form className="search-form" onSubmit={handleSubmit}>
        <div className="form-row">
          <div className="form-group">
            <label>Откуда</label>
            <input
              type="text"
              value={fromCity}
              onChange={(e) => setFromCity(e.target.value)}
              placeholder="Город отправления"
              required
            />
          </div>
          <div className="form-group">
            <label>Куда</label>
            <input
              type="text"
              value={toCity}
              onChange={(e) => setToCity(e.target.value)}
              placeholder="Город прибытия"
              required
            />
          </div>
          <div className="form-group">
            <label>Дата</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
            />
          </div>
          <button type="submit" className="btn btn-primary">
            Найти поездки
          </button>
        </div>
      </form>
    </div>
  );
}
