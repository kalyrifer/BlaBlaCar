"""Pydantic schemas package"""
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    LogoutResponse,
)
from app.schemas.user import (
    UserResponse,
    UserShortResponse,
    UserCreate,
    UserCreateInternal,
    UserUpdate,
    UserLoginRequest,
    UserLoginResponse,
)
from app.schemas.trip import (
    TripStatus,
    TripResponse,
    TripWithDriverResponse,
    TripDriverResponse,
    TripCreate,
    TripCreateInternal,
    TripUpdate,
    TripSearchFilters,
    PaginatedTripsResponse,
)
from app.schemas.request import (
    RequestStatus,
    TripRequestResponse,
    TripRequestPassengerResponse,
    TripRequestDriverResponse,
    RequestCreate,
    RequestCreateInternal,
    RequestStatusUpdate,
    PaginatedRequestsResponse,
)
from app.schemas.notification import (
    NotificationResponse,
    NotificationListResponse,
    NotificationCreate,
    NotificationMarkRead,
)

__all__ = [
    # Auth
    "RegisterRequest",
    "LoginRequest",
    "TokenResponse",
    "LogoutResponse",
    # User
    "UserResponse",
    "UserShortResponse",
    "UserCreate",
    "UserCreateInternal",
    "UserUpdate",
    "UserLoginRequest",
    "UserLoginResponse",
    # Trip
    "TripStatus",
    "TripResponse",
    "TripWithDriverResponse",
    "TripDriverResponse",
    "TripCreate",
    "TripCreateInternal",
    "TripUpdate",
    "TripSearchFilters",
    "PaginatedTripsResponse",
    # Request
    "RequestStatus",
    "TripRequestResponse",
    "TripRequestPassengerResponse",
    "TripRequestDriverResponse",
    "RequestCreate",
    "RequestCreateInternal",
    "RequestStatusUpdate",
    "PaginatedRequestsResponse",
    # Notification
    "NotificationResponse",
    "NotificationListResponse",
    "NotificationCreate",
    "NotificationMarkRead",
]
