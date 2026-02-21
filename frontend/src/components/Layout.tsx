import { Link, Outlet } from 'react-router-dom';
import { useAuthStore } from '../stores/auth';

export default function Layout() {
  const { isAuthenticated, user, logout } = useAuthStore();

  return (
    <div className="app">
      <header className="header">
        <div className="container header-content">
          <Link to="/" className="logo">
            🚗 BlaBlaCar
          </Link>
          <nav className="nav">
            {isAuthenticated ? (
              <>
                <Link to="/trips/new" className="btn btn-primary">
                  Создать поездку
                </Link>
                <Link to="/my-trips">Мои поездки</Link>
                <Link to="/notifications">Уведомления</Link>
                <Link to="/profile">{user?.name}</Link>
                <button onClick={logout} className="btn-link">Выйти</button>
              </>
            ) : (
              <>
                <Link to="/login">Войти</Link>
                <Link to="/register" className="btn btn-primary">Регистрация</Link>
              </>
            )}
          </nav>
        </div>
      </header>
      <main className="main">
        <div className="container">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
