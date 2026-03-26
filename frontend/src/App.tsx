import { Routes, Route, Navigate } from 'react-router-dom';
import { Suspense, lazy, useEffect } from 'react';
import { useAuthStore } from './stores/auth';
import Layout from './components/Layout';

// Lazy load pages for code splitting
const HomePage = lazy(() => import('./pages/HomePage'));
const TripsPage = lazy(() => import('./pages/TripsPage'));
const TripPage = lazy(() => import('./pages/TripPage'));
const CreateTripPage = lazy(() => import('./pages/CreateTripPage'));
const MyTripsPage = lazy(() => import('./pages/MyTripsPage'));
const LoginPage = lazy(() => import('./pages/LoginPage'));
const RegisterPage = lazy(() => import('./pages/RegisterPage'));
const ProfilePage = lazy(() => import('./pages/ProfilePage'));
const NotificationsPage = lazy(() => import('./pages/NotificationsPage'));

// Loading fallback component
function PageLoader() {
  return (
    <div className="loading-container">
      <div className="loading-spinner"></div>
    </div>
  );
}

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  
  if (isLoading) {
    return <PageLoader />;
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
    return <PageLoader />;
  }

  return (
    <Suspense fallback={<PageLoader />}>
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
    </Suspense>
  );
}

export default App;
