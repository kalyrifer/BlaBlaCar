"""Mappers between schemas and ORM models"""
from datetime import datetime
from uuid import UUID
from typing import Optional

from app.schemas.user import (
    UserResponse, 
    UserShortResponse, 
    UserCreate, 
    UserCreateInternal,
    UserUpdate
)
from app.schemas.trip import (
    TripResponse, 
    TripWithDriverResponse, 
    TripCreate, 
    TripCreateInternal,
    TripUpdate,
    TripDriverResponse
)
from app.schemas.request import (
    TripRequestResponse,
    TripRequestPassengerResponse,
    TripRequestDriverResponse,
    RequestCreate,
    RequestCreateInternal,
    RequestStatusUpdate
)
from app.schemas.notification import (
    NotificationResponse,
    NotificationCreate
)


# ================== User Mappers ==================

def user_orm_to_response(user_orm) -> UserResponse:
    """Map User ORM to UserResponse"""
    return UserResponse(
        id=user_orm.id,
        email=user_orm.email,
        name=user_orm.name,
        phone=user_orm.phone,
        avatar_url=user_orm.avatar_url,
        rating=user_orm.rating,
        created_at=user_orm.created_at
    )


def user_orm_to_short_response(user_orm) -> UserShortResponse:
    """Map User ORM to UserShortResponse"""
    return UserShortResponse(
        id=user_orm.id,
        name=user_orm.name,
        avatar_url=user_orm.avatar_url,
        rating=user_orm.rating,
        phone=user_orm.phone
    )


def user_create_to_internal(user_create: UserCreate, password_hash: str) -> UserCreateInternal:
    """Map UserCreate to UserCreateInternal (for service layer)"""
    return UserCreateInternal(
        email=user_create.email,
        password_hash=password_hash,
        name=user_create.name,
        phone=user_create.phone
    )


def user_update_to_dict(user_update: UserUpdate) -> dict:
    """Map UserUpdate to dict for repository"""
    return user_update.model_dump(exclude_unset=True)


# ================== Trip Mappers ==================

def trip_orm_to_response(trip_orm) -> TripResponse:
    """Map Trip ORM to TripResponse"""
    return TripResponse(
        id=trip_orm.id,
        driver_id=trip_orm.driver_id,
        from_city=trip_orm.from_city,
        to_city=trip_orm.to_city,
        departure_date=trip_orm.departure_date,
        departure_time=trip_orm.departure_time,
        available_seats=trip_orm.available_seats,
        price_per_seat=trip_orm.price_per_seat,
        description=trip_orm.description,
        status=trip_orm.status,
        created_at=trip_orm.created_at
    )


def trip_orm_to_with_driver_response(trip_orm, driver_orm=None) -> TripWithDriverResponse:
    """Map Trip ORM to TripWithDriverResponse"""
    driver_data = None
    if driver_orm:
        driver_data = {
            "id": str(driver_orm.id),
            "name": driver_orm.name,
            "avatar_url": driver_orm.avatar_url,
            "rating": driver_orm.rating
        }
    
    return TripWithDriverResponse(
        id=trip_orm.id,
        driver_id=trip_orm.driver_id,
        driver=driver_data,
        from_city=trip_orm.from_city,
        to_city=trip_orm.to_city,
        departure_date=trip_orm.departure_date,
        departure_time=trip_orm.departure_time,
        available_seats=trip_orm.available_seats,
        price_per_seat=trip_orm.price_per_seat,
        status=trip_orm.status
    )


def trip_orm_to_driver_response(trip_orm, passenger_count: int = 0) -> TripDriverResponse:
    """Map Trip ORM to TripDriverResponse"""
    return TripDriverResponse(
        id=trip_orm.id,
        from_city=trip_orm.from_city,
        to_city=trip_orm.to_city,
        departure_date=trip_orm.departure_date,
        departure_time=trip_orm.departure_time,
        available_seats=trip_orm.available_seats,
        price_per_seat=trip_orm.price_per_seat,
        status=trip_orm.status,
        passengers_count=passenger_count
    )


def trip_create_to_internal(trip_create: TripCreate, driver_id: UUID) -> TripCreateInternal:
    """Map TripCreate to TripCreateInternal (for service layer)"""
    return TripCreateInternal(
        driver_id=driver_id,
        from_city=trip_create.from_city,
        to_city=trip_create.to_city,
        departure_date=trip_create.departure_date,
        departure_time=trip_create.departure_time,
        available_seats=trip_create.available_seats,
        price_per_seat=trip_create.price_per_seat,
        description=trip_create.description,
        status="active"
    )


def trip_update_to_dict(trip_update: TripUpdate) -> dict:
    """Map TripUpdate to dict for repository"""
    return trip_update.model_dump(exclude_unset=True)


# ================== Request Mappers ==================

def request_orm_to_response(request_orm, passenger_orm=None) -> TripRequestResponse:
    """Map TripRequest ORM to TripRequestResponse"""
    passenger_data = None
    if passenger_orm:
        passenger_data = {
            "id": str(passenger_orm.id),
            "name": passenger_orm.name,
            "avatar_url": passenger_orm.avatar_url,
            "rating": passenger_orm.rating,
            "phone": passenger_orm.phone
        }
    
    return TripRequestResponse(
        id=request_orm.id,
        trip_id=request_orm.trip_id,
        passenger_id=request_orm.passenger_id,
        passenger=passenger_data,
        seats_requested=request_orm.seats_requested,
        message=request_orm.message,
        status=request_orm.status,
        created_at=request_orm.created_at,
        updated_at=request_orm.updated_at
    )


def request_orm_to_passenger_response(request_orm, trip_orm=None, driver_orm=None) -> TripRequestPassengerResponse:
    """Map TripRequest ORM to TripRequestPassengerResponse"""
    trip_data = None
    if trip_orm:
        trip_data = {
            "id": str(trip_orm.id),
            "from_city": trip_orm.from_city,
            "to_city": trip_orm.to_city,
            "departure_date": trip_orm.departure_date,
            "departure_time": trip_orm.departure_time,
            "driver_name": driver_orm.name if driver_orm else None
        }
    
    return TripRequestPassengerResponse(
        id=request_orm.id,
        trip_id=request_orm.trip_id,
        trip=trip_data,
        seats_requested=request_orm.seats_requested,
        status=request_orm.status,
        created_at=request_orm.created_at
    )


def request_orm_to_driver_response(request_orm, passenger_orm=None) -> TripRequestDriverResponse:
    """Map TripRequest ORM to TripRequestDriverResponse"""
    passenger_data = None
    if passenger_orm:
        passenger_data = {
            "id": str(passenger_orm.id),
            "name": passenger_orm.name,
            "avatar_url": passenger_orm.avatar_url,
            "rating": passenger_orm.rating,
            "phone": passenger_orm.phone
        }
    
    return TripRequestDriverResponse(
        id=request_orm.id,
        passenger_id=request_orm.passenger_id,
        passenger=passenger_data,
        seats_requested=request_orm.seats_requested,
        message=request_orm.message,
        status=request_orm.status,
        created_at=request_orm.created_at
    )


def request_create_to_internal(
    request_create: RequestCreate, 
    passenger_id: UUID
) -> RequestCreateInternal:
    """Map RequestCreate to RequestCreateInternal (for service layer)"""
    return RequestCreateInternal(
        trip_id=request_create.trip_id,
        passenger_id=passenger_id,
        seats_requested=request_create.seats_requested,
        message=request_create.message,
        status="pending"
    )


def request_status_update_to_str(status_update: RequestStatusUpdate) -> str:
    """Map RequestStatusUpdate to string for repository"""
    return status_update.status


# ================== Notification Mappers ==================

def notification_orm_to_response(notification_orm) -> NotificationResponse:
    """Map Notification ORM to NotificationResponse"""
    return NotificationResponse(
        id=notification_orm.id,
        user_id=notification_orm.user_id,
        type=notification_orm.type,
        title=notification_orm.title,
        message=notification_orm.message,
        related_trip_id=notification_orm.related_trip_id,
        related_request_id=notification_orm.related_request_id,
        is_read=notification_orm.is_read,
        created_at=notification_orm.created_at
    )


def notification_create_to_dict(notification_create: NotificationCreate) -> dict:
    """Map NotificationCreate to dict for repository"""
    return notification_create.model_dump()