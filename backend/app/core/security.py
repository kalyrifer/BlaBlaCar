"""
Функции для работы с безопасностью: пароли, JWT.
"""
import logging
import secrets
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Set
from uuid import UUID
from pathlib import Path
from jose import JWTError, jwt
from cryptography.hazmat.primitives.asymmetric import rsa
import bcrypt

from app.core.config import settings

logger = logging.getLogger(__name__)

# Thread pool for async-safe hashing
_hash_executor = ThreadPoolExecutor(max_workers=2)

# Token blacklist (in-memory, can be moved to Redis for production)
_token_blacklist: Set[str] = set()

# RSA keys cache
_rsa_private_key: Optional[Any] = None
_rsa_public_key: Optional[Any] = None


def _load_rsa_keys() -> tuple[Any, Any]:
    """Load RSA keys from files or fall back to HMAC for development."""
    global _rsa_private_key, _rsa_public_key
    
    private_key_path = Path(settings.JWT_PRIVATE_KEY_PATH)
    public_key_path = Path(settings.JWT_PUBLIC_KEY_PATH)
    
    if private_key_path.exists() and public_key_path.exists():
        try:
            # Load private key
            with open(private_key_path, 'rb') as f:
                from cryptography.hazmat.primitives import serialization
                from cryptography.hazmat.backends import default_backend
                _rsa_private_key = serialization.load_pem_private_key(
                    f.read(),
                    password=None,
                    backend=default_backend()
                )
            
            # Load public key
            with open(public_key_path, 'rb') as f:
                _rsa_public_key = serialization.load_pem_public_key(
                    f.read(),
                    backend=default_backend()
                )
            
            logger.info("RSA keys loaded successfully, using RS256")
            return _rsa_private_key, _rsa_public_key
        except Exception as e:
            logger.warning(f"Failed to load RSA keys: {e}, falling back to HS256")
    
    # Fallback to HMAC for development
    return None, None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверить пароль"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    """Хешировать пароль"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def is_token_blacklisted(token: str) -> bool:
    """Проверить, находится ли токен в blacklist."""
    return token in _token_blacklist


def add_to_blacklist(token: str) -> None:
    """Добавить токен в blacklist."""
    _token_blacklist.add(token)
    logger.info("Token added to blacklist")


def create_access_token(data: Dict[str, Any], exp_minutes: int = None) -> str:
    """Создать JWT access токен (короткоживущий) с RS256
    
    Args:
        data: Данные для токена (например, {"sub": user_id})
        exp_minutes: Срок жизни токена в минутах (по умолчанию 15 минут)
    
    Returns:
        Закодированный JWT токен
    """
    if exp_minutes is None:
        exp_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=exp_minutes)
    to_encode.update({"exp": expire, "type": "access"})
    
    # Try RS256 first, fallback to HS256
    private_key, _ = _load_rsa_keys()
    
    if private_key is not None:
        encoded_jwt = jwt.encode(
            to_encode,
            private_key,
            algorithm="RS256"
        )
    else:
        # Fallback to HS256 for development
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            algorithm="HS256"
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
    
    # Hash the token for storage
    hashed_token = bcrypt.hashpw(raw_token.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    return raw_token, hashed_token


def verify_refresh_token(plain_token: str, hashed_token: str) -> bool:
    """Проверить refresh токен
    
    Args:
        plain_token: Оригинальный токен от клиента
        hashed_token: Хешированный токен из хранилища
        
    Returns:
        True если токен валиден
    """
    return bcrypt.checkpw(plain_token.encode('utf-8'), hashed_token.encode('utf-8'))


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """Декодировать токен с проверкой blacklist."""
    # Check blacklist first
    if is_token_blacklisted(token):
        logger.warning("Attempted to use blacklisted token")
        return None
    
    try:
        # Try RS256 first, fallback to HS256
        _, public_key = _load_rsa_keys()
        
        if public_key is not None:
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"]
            )
        else:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=["HS256"]
            )
        return payload
    except JWTError as e:
        logger.debug(f"Token decode error: {e}")
        return None
