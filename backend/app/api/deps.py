"""Зависимости для API endpoints"""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.trip_service import TripService
from app.services.request_service import RequestService

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
    
    db = get_db()
    user = await db.users.get_by_id(UUID(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


async def get_auth_service() -> AuthService:
    """Получить экземпляр AuthService"""
    db = get_db()
    return AuthService(user_repo=db.users)


async def get_trip_service() -> TripService:
    """Получить экземпляр TripService"""
    db = get_db()
    return TripService(trip_repo=db.trips, user_repo=db.users)


async def get_request_service() -> RequestService:
    """Получить экземпляр RequestService"""
    db = get_db()
    return RequestService(
        request_repo=db.requests,
        trip_repo=db.trips,
        notification_repo=db.notifications,
        user_repo=db.users
    )
