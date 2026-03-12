"""
Функции для работы с безопасностью: пароли, JWT.
"""
import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import UUID
from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Thread pool for async-safe hashing
_hash_executor = ThreadPoolExecutor(max_workers=2)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Хешировать пароль"""
    return pwd_context.hash(password)


def create_access_token(data: Dict[str, Any], exp_minutes: int = 15) -> str:
    """Создать JWT access токен (короткоживущий)
    
    Args:
        data: Данные для токена (например, {"sub": user_id})
        exp_minutes: Срок жизни токена в минутах (по умолчанию 15 минут)
    
    Returns:
        Закодированный JWT токен
    """
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=exp_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.JWT_SECRET_KEY, 
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(user_id: UUID) -> tuple[str, str]:
    """Создать refresh токен
    
    Генерирует безопасный случайный токен и возвращает его хешированную версию
    для хранения и оригинальную версию для клиента.
    
    Args:
        user_id: ID пользователя
        
    Returns:
        Кортеж (raw_token, hashed_token) - оригинальный токен для клиента и хеш для хранения
    """
    # Generate secure random token
    raw_token = secrets.token_urlsafe(32)
    
    # Hash the token for storage (using sync hashing in thread pool)
    def hash_token():
        return pwd_context.hash(raw_token)
    
    future = _hash_executor.submit(hash_token)
    hashed_token = future.result()
    
    return raw_token, hashed_token


def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    """Проверить refresh токен
    
    Args:
        plain_token: Оригинальный токен от клиента
        hashed_token: Хешированный токен из хранилища
        
    Returns:
        True если токен валиден
    """
    return pwd_context.verify(plain_token, hashed_token)


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодировать токен"""
    try:
        payload = jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None
