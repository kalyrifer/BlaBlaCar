"""Fixtures for tests - in-memory repositories and service DI"""
import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from typing import AsyncGenerator

# Configure pytest-asyncio
pytest_plugins = ('pytest_asyncio',)

from app.repositories.inmemory import (
    InMemoryUserRepository,
    InMemoryTripRepository,
    InMemoryRequestRepository,
    InMemoryNotificationRepository,
    InMemoryRefreshTokenRepository,
)
from app.repositories.inmemory.locks import LockManager
from app.services.auth_service import AuthService
from app.services.trip_service import TripService
from app.services.request_service import RequestService


class InMemoryDatabase:
    """In-memory database for testing"""
    
    def __init__(self):
        self.users = InMemoryUserRepository()
        self.trips = InMemoryTripRepository()
        self.requests = InMemoryRequestRepository()
        self.notifications = InMemoryNotificationRepository()
        self.refresh_tokens = InMemoryRefreshTokenRepository()
        self.lock_manager = LockManager()
    
    async def close(self):
        """Clean up resources"""
        self.lock_manager.clear_locks()


@pytest.fixture(scope="function")
def db() -> InMemoryDatabase:
    """Create a fresh in-memory database for each test"""
    return InMemoryDatabase()


@pytest.fixture(scope="function")
def auth_service(db: InMemoryDatabase) -> AuthService:
    """Create AuthService with in-memory user repository"""
    return AuthService(user_repo=db.users)


@pytest.fixture(scope="function")
def trip_service(db: InMemoryDatabase) -> TripService:
    """Create TripService with in-memory repositories"""
    return TripService(trip_repo=db.trips, user_repo=db.users)


@pytest.fixture(scope="function")
def request_service(db: InMemoryDatabase) -> RequestService:
    """Create RequestService with in-memory repositories"""
    return RequestService(
        request_repo=db.requests,
        trip_repo=db.trips,
        notification_repo=db.notifications,
        user_repo=db.users,
        lock_manager=db.lock_manager
    )


@pytest.fixture(scope="function")
async def test_user(db: InMemoryDatabase) -> dict:
    """Create a test user"""
    user_data = {
        "email": "test@example.com",
        "password_hash": "hashed_password",
        "name": "Test User",
        "phone": "+1234567890"
    }
    user = await db.users.create(user_data)
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "phone": user.phone
    }


@pytest.fixture(scope="function")
async def test_driver(db: InMemoryDatabase) -> dict:
    """Create a test driver"""
    user_data = {
        "email": "driver@example.com",
        "password_hash": "hashed_password",
        "name": "Driver User",
        "phone": "+1234567891"
    }
    user = await db.users.create(user_data)
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "phone": user.phone
    }


@pytest.fixture(scope="function")
async def test_passenger(db: InMemoryDatabase) -> dict:
    """Create a test passenger"""
    user_data = {
        "email": "passenger@example.com",
        "password_hash": "hashed_password",
        "name": "Passenger User",
        "phone": "+1234567892"
    }
    user = await db.users.create(user_data)
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "phone": user.phone
    }


@pytest.fixture(scope="function")
async def test_trip(db: InMemoryDatabase, test_driver: dict) -> dict:
    """Create a test trip"""
    from uuid import UUID
    trip_data = {
        "driver_id": UUID(test_driver["id"]),
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_at": datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
        "available_seats": 3,
        "price_per_seat": 1500,
        "description": "Comfortable trip",
        "status": "active"
    }
    trip = await db.trips.create(trip_data)
    return {
        "id": str(trip.id),
        "driver_id": str(trip.driver_id),
        "from_city": trip.from_city,
        "to_city": trip.to_city,
        "available_seats": trip.available_seats,
        "price_per_seat": trip.price_per_seat,
        "status": trip.status
    }


@pytest.fixture(scope="function")
async def test_trip_one_seat(db: InMemoryDatabase, test_driver: dict) -> dict:
    """Create a test trip with only 1 seat"""
    from uuid import UUID
    trip_data = {
        "driver_id": UUID(test_driver["id"]),
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_at": datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
        "available_seats": 1,
        "price_per_seat": 1500,
        "description": "Trip with one seat",
        "status": "active"
    }
    trip = await db.trips.create(trip_data)
    return {
        "id": str(trip.id),
        "driver_id": str(trip.driver_id),
        "from_city": trip.from_city,
        "to_city": trip.to_city,
        "available_seats": trip.available_seats,
        "price_per_seat": trip.price_per_seat,
        "status": trip.status
    }
