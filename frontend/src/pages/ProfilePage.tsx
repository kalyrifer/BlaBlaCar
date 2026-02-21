import { useAuthStore } from '../stores/auth';

export default function ProfilePage() {
  const { user } = useAuthStore();

  if (!user) return <div>Загрузка...</div>;

  return (
    <div className="profile-page">
      <h1>Профиль</h1>
      
      <div className="profile-info">
        <div className="profile-avatar">
          {user.name.charAt(0).toUpperCase()}
        </div>
        
        <div className="profile-details">
          <h2>{user.name}</h2>
          <p>Email: {user.email}</p>
          {user.phone && <p>Телефон: {user.phone}</p>}
          {user.rating && <p>Рейтинг: ★ {user.rating}</p>}
        </div>
      </div>
    </div>
  );
}
