import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import heroImage from '../../photo-1768162485233-8aa1f27386fe.jpg';
import roadImage from '../../photo-1767700871853-037a9dc30e81.jpg';

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

  const features = [
    {
      title: 'Гибкие маршруты',
      description: 'Добавляйте остановки и встречи на карте.',
    },
    {
      title: 'Умный поиск',
      description: 'Находите попутчиков по маршруту и времени.',
    },
    {
      title: 'Доверие к водителю',
      description: 'Отзывы и рейтинги помогут выбрать надёжного водителя.',
    },
    {
      title: 'Гибкие заявки',
      description: 'Отправляйте запросы на бронирование места.',
    },
    {
      title: 'Планирование в пару кликов',
      description: 'Создавайте и находите поездки быстро и легко.',
    },
  ];

  const steps = [
    {
      number: '01',
      title: 'Найдите поездку',
      description: 'Укажите город отправления, прибытия и дату.',
    },
    {
      number: '02',
      title: 'Оставьте заявку',
      description: 'Отправьте запрос водителю на бронирование места.',
    },
    {
      number: '03',
      title: 'Подтвердите детали',
      description: 'Свяжитесь с водителем и договоритесь о поездке.',
    },
  ];

  return (
    <div className="home-page">
      {/* Hero Section - Image on right */}
      <section className="hero-side-by-side">
        <div className="hero-content">
          <span className="hero-label">Попутчики без лишнего шума</span>
          <h1 className="hero-title">
            RoadMate — ваш быстрый способ найти попутчиков и разделить дорогу.
          </h1>
          <p className="hero-subtitle">
            Мы соединяем водителей и пассажиров для удобных и выгодных поездок.
          </p>
        </div>
        <div className="hero-image-container">
          <img src={heroImage} alt="Парковка" className="hero-image" />
        </div>
      </section>

      {/* Features Grid */}
      <section className="features">
        {features.map((feature, index) => (
          <div key={index} className="feature">
            <h3 className="feature-title">{feature.title}</h3>
            <p className="feature-description">{feature.description}</p>
          </div>
        ))}
      </section>

      {/* How it Works - Image on left */}
      <section className="how-it-works-side-by-side">
        <div className="how-it-works-image-container">
          <img src={roadImage} alt="Дорога" className="section-image" />
        </div>
        <div className="how-it-works-content">
          <h2 className="section-title">Как это работает</h2>
          <div className="steps">
            {steps.map((step, index) => (
              <div key={index} className="step">
                <span className="step-number">{step.number}</span>
                <div className="step-content">
                  <h3 className="step-title">{step.title}</h3>
                  <p className="step-description">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <h2 className="cta-title">Готовы стартовать?</h2>
        <p className="cta-subtitle">
          Забронируйте место или создайте свой маршрут уже сейчас.
        </p>
        <form onSubmit={handleSubmit} className="cta-form">
          <div className="cta-form-row">
            <input
              type="text"
              placeholder="Откуда"
              value={searchData.from_city}
              onChange={(e) => setSearchData({ ...searchData, from_city: e.target.value })}
              className="cta-input"
            />
            <input
              type="text"
              placeholder="Куда"
              value={searchData.to_city}
              onChange={(e) => setSearchData({ ...searchData, to_city: e.target.value })}
              className="cta-input"
            />
            <input
              type="date"
              value={searchData.date}
              onChange={(e) => setSearchData({ ...searchData, date: e.target.value })}
              className="cta-input"
            />
            <button type="submit" className="cta-button">
              Найти поездку
            </button>
          </div>
        </form>
      </section>
    </div>
  );
}
