"""Auth Service - бизнес-логика аутентификации"""
from uuid import UUID
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError
from app.repositories.interfaces import IUserRepository
from app.core.logger import get_logger, get_request_id

logger = get_logger(__name__)


class UserCreate(BaseModel):
    """Схема для создания пользователя"""
    email: EmailStr
    password: str
    name: str
    phone: str


class UserResponse(BaseModel):
    """Схема ответа пользователя"""
    id: str
    email: str
    name: str
    phone: str
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    created_at: str


class TokenResponse(BaseModel):
    """Схема ответа токена"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class AuthService:
    """Сервис для работы с аутентификацией"""
    
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo
    
    async def register(self, user_create: UserCreate) -> UserResponse:
        """Регистрация нового пользователя"""
        request_id = get_request_id()
        
        logger.info(
            "User registration started",
            extra={
                "email": user_create.email,
                "user_id": None,
            }
        )
        
        # Проверка, что email уже не существует
        existing = await self._user_repo.get_by_email(user_create.email)
        if existing:
            logger.warning(
                "User registration failed - email already exists",
                extra={"email": user_create.email, "request_id": request_id}
            )
            raise UserAlreadyExistsError("Email already registered")
        
        # Создание пользователя
        user = await self._user_repo.create({
            "email": user_create.email,
            "password_hash": get_password_hash(user_create.password),
            "name": user_create.name,
            "phone": user_create.phone
        })
        
        logger.info(
            "User registered successfully",
            extra={
                "user_id": str(user.id),
                "email": user.email,
            }
        )
        
        return UserResponse(
            id=str(user.id),
            email=user.email,
            name=user.name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            rating=user.rating,
            created_at=user.created_at.isoformat()
        )
    
    async def login(self, email: str, password: str) -> TokenResponse:
        """Вход пользователя"""
        request_id = get_request_id()
        
        logger.info(
            "User login started",
            extra={"email": email}
        )
        
        user = await self._user_repo.get_by_email(email)
        
        if not user or not verify_password(password, user.password_hash):
            logger.warning(
                "User login failed - invalid credentials",
                extra={"email": email, "request_id": request_id}
            )
            raise InvalidCredentialsError("Invalid credentials")
        
        # Генерация токена
        access_token = create_access_token({
            "sub": str(user.id),
            "email": user.email,
            "name": user.name
        })
        
        logger.info(
            "User logged in successfully",
            extra={"user_id": str(user.id), "email": user.email}
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse(
                id=str(user.id),
                email=user.email,
                name=user.name,
                phone=user.phone,
                avatar_url=user.avatar_url,
                rating=user.rating,
                created_at=user.created_at.isoformat()
            )
        )