import { Link, useLocation, Outlet } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';

export default function Layout() {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <Link to="/" className="logo">
              RoadMate
            </Link>
            
            <nav className="nav nav-center">
              <Link to="/trips" className={location.pathname === '/trips' ? 'active' : ''}>
                Поиск
              </Link>
              <Link to="/trips/new" className={location.pathname === '/trips/new' ? 'active' : ''}>
                Создать
              </Link>
              <Link to="/my-trips" className={location.pathname === '/my-trips' ? 'active' : ''}>
                Заявки
              </Link>
              <Link to="/profile" className={location.pathname === '/profile' ? 'active' : ''}>
                Профиль
              </Link>
              <Link to="/messages" className={location.pathname === '/messages' ? 'active' : ''} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span>Чаты</span>
              </Link>
            </nav>
            
            <nav className="nav nav-right">
              {!isAuthenticated && (
                <>
                  <Link to="/login" className={location.pathname === '/login' ? 'active' : ''}>
                    Войти
                  </Link>
                  <Link to="/register" className="btn btn-primary btn-sm">
                    Регистрация
                  </Link>
                </>
              )}
            </nav>
          </div>
        </div>
      </header>
      
      <main className="main-content">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
