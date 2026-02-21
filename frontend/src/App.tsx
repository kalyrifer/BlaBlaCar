import { Routes, Route, Navigate } from 'react-router-dom';
import { useEffect } from 'react';
import { useAuthStore } from './stores/auth';
import Layout from './components/Layout';
import HomePage from './pages/HomePage';
import TripsPage from './pages/TripsPage';
import TripPage from './pages/TripPage';
import CreateTripPage from './pages/CreateTripPage';
import MyTripsPage from './pages/MyTripsPage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ProfilePage from './pages/ProfilePage';
import NotificationsPage from './pages/NotificationsPage';

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) {
    return <div>Загрузка...</div>;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  const { checkAuth, isLoading } = useAuthStore();
  
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);
  
  if (isLoading) {
    return <div>Загрузка...</div>;
  }
  
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="trips" element={<TripsPage />} />
        <Route path="trips/:id" element={<TripPage />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        <Route path="profile/:id?" element={<ProfilePage />} />
        
        <Route path="trips/new" element={
          <ProtectedRoute>
            <CreateTripPage />
          </ProtectedRoute>
        } />
        <Route path="my-trips" element={
          <ProtectedRoute>
            <MyTripsPage />
          </ProtectedRoute>
        } />
        <Route path="notifications" element={
          <ProtectedRoute>
            <NotificationsPage />
          </ProtectedRoute>
        } />
      </Route>
    </Routes>
  );
}

export default App;
