import { Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';

export default function Layout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user, logout } = useAuthStore();
  const location = useLocation();

  return (
    <div className="app">
      <header className="header">
        <div className="container">
          <div className="header-content">
            <Link to="/" className="logo">
              🚗 BlaBlaCar
            </Link>
            
            <nav className="nav">
              <Link 
                to="/" 
                className={location.pathname === '/' ? 'active' : ''}
              >
                Поиск
              </Link>
              
              {isAuthenticated && (
                <>
                  <Link 
                    to="/create-trip" 
                    className={location.pathname === '/create-trip' ? 'active' : ''}
                  >
                    Создать поездку
                  </Link>
                  <Link 
                    to="/my-trips" 
                    className={location.pathname === '/my-trips' ? 'active' : ''}
                  >
                    Мои поездки
                  </Link>
                  <Link 
                    to="/notifications" 
                    className={location.pathname === '/notifications' ? 'active' : ''}
                  >
                    🔔
                  </Link>
                  <Link 
                    to="/profile" 
                    className={location.pathname === '/profile' ? 'active' : ''}
                  >
                    👤 {user?.name}
                  </Link>
                  <button onClick={logout} className="btn btn-secondary btn-sm">
                    Выйти
                  </button>
                </>
              )}
              
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
          {children}
        </div>
      </main>
    </div>
  );
}
