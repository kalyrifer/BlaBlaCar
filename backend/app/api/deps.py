"""Зависимости для API endpoints"""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db, get_user_repo, get_trip_repo, get_request_repo, get_notification_repo, get_refresh_token_repo
from app.core.security import decode_token
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.trip_service import TripService
from app.services.request_service import RequestService
from app.repositories.interfaces import IRefreshTokenRepository

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Получить текущего пользователя из токена"""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user_repo = get_user_repo()
    user = await user_repo.get_by_id(UUID(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_auth_service() -> AuthService:
    """Получить экземпляр AuthService"""
    user_repo = get_user_repo()
    return AuthService(user_repo=user_repo)


async def get_trip_service() -> TripService:
    """Получить экземпляр TripService"""
    trip_repo = get_trip_repo()
    user_repo = get_user_repo()
    return TripService(trip_repo=trip_repo, user_repo=user_repo)


async def get_request_service() -> RequestService:
    """Получить экземпляр RequestService"""
    request_repo = get_request_repo()
    trip_repo = get_trip_repo()
    notification_repo = get_notification_repo()
    user_repo = get_user_repo()
    return RequestService(
        request_repo=request_repo,
        trip_repo=trip_repo,
        notification_repo=notification_repo,
        user_repo=user_repo
    )


async def get_refresh_token_repo() -> IRefreshTokenRepository:
    """Получить экземпляр RefreshTokenRepository"""
    return get_refresh_token_repo()
