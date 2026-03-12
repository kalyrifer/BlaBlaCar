"""Тесты для AuthService"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID
from datetime import datetime

from app.services.auth_service import AuthService, UserCreate


# Mock User Repository
class MockUserRepository:
    def __init__(self):
        self.users = {}
    
    async def create(self, user_data: dict):
        from app.models.user import User
        user = User(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            name=user_data["name"],
            phone=user_data["phone"],
            avatar_url=None,
            rating=None,
            created_at=datetime.now()
        )
        self.users[user.email] = user
        return user
    
    async def get_by_id(self, user_id: UUID):
        for user in self.users.values():
            if user.id == user_id:
                return user
        return None
    
    async def get_by_email(self, email: str):
        return self.users.get(email)
    
    async def update(self, user_id: UUID, user_data: dict):
        pass
    
    async def delete(self, user_id: UUID) -> bool:
        return True
    
    async def list_all(self):
        return list(self.users.values())


# Mock password hashing functions
@pytest.fixture
def mock_security():
    """Mock security functions"""
    with patch('app.services.auth_service.get_password_hash') as mock_hash, \
         patch('app.services.auth_service.verify_password') as mock_verify, \
         patch('app.services.auth_service.create_access_token') as mock_token:
        
        # Mock password hash - return a simple hash
        mock_hash.return_value = "hashed_password"
        
        # Mock verify - return True only for "password123"
        def verify_side_effect(plain, hashed):
            return plain == "password123"
        mock_verify.side_effect = verify_side_effect
        
        # Mock token - return a simple token
        mock_token.return_value = "test_token_123"
        
        yield {
            "hash": mock_hash,
            "verify": mock_verify,
            "token": mock_token
        }


@pytest.mark.asyncio
class TestAuthService:
    
    async def test_register_success(self, mock_security):
        """Тест успешной регистрации"""
        user_repo = MockUserRepository()
        auth_service = AuthService(user_repo)
        
        user_create = UserCreate(
            email="test@example.com",
            password="password123",
            name="Test User",
            phone="+1234567890"
        )
        
        result = await auth_service.register(user_create)
        
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        assert result.phone == "+1234567890"
        assert result.id is not None
        mock_security["hash"].assert_called_once_with("password123")
    
    async def test_register_duplicate_email(self, mock_security):
        """Тест регистрации с уже существующим email"""
        user_repo = MockUserRepository()
        auth_service = AuthService(user_repo)
        
        # Создаем первого пользователя
        user_create = UserCreate(
            email="test@example.com",
            password="password123",
            name="Test User",
            phone="+1234567890"
        )
        await auth_service.register(user_create)
        
        # Пытаемся зарегистрировать того же пользователя
        with pytest.raises(ValueError, match="Email already registered"):
            await auth_service.register(user_create)
    
    async def test_login_success(self, mock_security):
        """Тест успешного входа"""
        user_repo = MockUserRepository()
        auth_service = AuthService(user_repo)
        
        # Регистрируем пользователя
        user_create = UserCreate(
            email="test@example.com",
            password="password123",
            name="Test User",
            phone="+1234567890"
        )
        await auth_service.register(user_create)
        
        # Входим
        result = await auth_service.login("test@example.com", "password123")
        
        assert result.access_token is not None
        assert result.token_type == "bearer"
        assert result.user.email == "test@example.com"
    
    async def test_login_invalid_credentials(self, mock_security):
        """Тест входа с неверными данными"""
        user_repo = MockUserRepository()
        auth_service = AuthService(user_repo)
        
        # Неверный пароль
        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.login("test@example.com", "wrongpassword")
    
    async def test_login_nonexistent_user(self, mock_security):
        """Тест входа с несуществующим пользователем"""
        user_repo = MockUserRepository()
        auth_service = AuthService(user_repo)
        
        with pytest.raises(ValueError, match="Invalid credentials"):
            await auth_service.login("nonexistent@example.com", "password123")