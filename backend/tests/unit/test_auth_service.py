"""Unit tests for AuthService - register and login"""
import pytest
from unittest.mock import patch
from uuid import uuid4

from app.services.auth_service import AuthService, UserCreate
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError


# Mock password hashing and token functions
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
class TestAuthServiceRegister:
    """Tests for AuthService.register"""
    
    async def test_register_success(self, auth_service: AuthService, mock_security):
        """Test successful user registration"""
        user_create = UserCreate(
            email="newuser@example.com",
            password="password123",
            name="New User",
            phone="+1234567890"
        )
        
        result = await auth_service.register(user_create)
        
        assert result.email == "newuser@example.com"
        assert result.name == "New User"
        assert result.phone == "+1234567890"
        assert result.id is not None
        mock_security["hash"].assert_called_once_with("password123")
    
    async def test_register_duplicate_email(self, auth_service: AuthService, mock_security, db):
        """Test registration with existing email raises error"""
        # Create initial user
        user_create = UserCreate(
            email="existing@example.com",
            password="password123",
            name="Existing User",
            phone="+1234567890"
        )
        await auth_service.register(user_create)
        
        # Try to register with same email
        with pytest.raises(UserAlreadyExistsError, match="Email already registered"):
            await auth_service.register(user_create)
    
    async def test_register_multiple_users(self, auth_service: AuthService, mock_security):
        """Test registering multiple different users"""
        user1 = UserCreate(
            email="user1@example.com",
            password="password123",
            name="User One",
            phone="+1111111111"
        )
        user2 = UserCreate(
            email="user2@example.com",
            password="password123",
            name="User Two",
            phone="+2222222222"
        )
        
        result1 = await auth_service.register(user1)
        result2 = await auth_service.register(user2)
        
        assert result1.email == "user1@example.com"
        assert result2.email == "user2@example.com"
        assert result1.id != result2.id


@pytest.mark.asyncio
class TestAuthServiceLogin:
    """Tests for AuthService.login"""
    
    async def test_login_success(self, auth_service: AuthService, mock_security, db):
        """Test successful user login"""
        # First register a user
        user_create = UserCreate(
            email="loginuser@example.com",
            password="password123",
            name="Login User",
            phone="+1234567890"
        )
        await auth_service.register(user_create)
        
        # Then login
        result = await auth_service.login("loginuser@example.com", "password123")
        
        assert result.access_token == "test_token_123"
        assert result.token_type == "bearer"
        assert result.user.email == "loginuser@example.com"
        assert result.user.name == "Login User"
    
    async def test_login_invalid_password(self, auth_service: AuthService, mock_security, db):
        """Test login with invalid password"""
        # Register user
        user_create = UserCreate(
            email="passuser@example.com",
            password="password123",
            name="Password User",
            phone="+1234567890"
        )
        await auth_service.register(user_create)
        
        # Try login with wrong password
        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await auth_service.login("passuser@example.com", "wrongpassword")
    
    async def test_login_nonexistent_user(self, auth_service: AuthService, mock_security):
        """Test login with non-existent user"""
        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await auth_service.login("nonexistent@example.com", "password123")
    
    async def test_login_empty_email(self, auth_service: AuthService, mock_security):
        """Test login with empty email"""
        with pytest.raises(InvalidCredentialsError, match="Invalid credentials"):
            await auth_service.login("", "password123")
