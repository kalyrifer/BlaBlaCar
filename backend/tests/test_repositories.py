"""Tests for in-memory repositories"""
import pytest
import asyncio
from uuid import uuid4

from app.repositories.inmemory import (
    InMemoryUserRepository,
    InMemoryTripRepository,
    InMemoryRequestRepository,
    InMemoryNotificationRepository,
    InMemoryRefreshTokenRepository,
)


@pytest.fixture
def user_repo():
    return InMemoryUserRepository()


@pytest.fixture
def trip_repo():
    return InMemoryTripRepository()


@pytest.fixture
def request_repo():
    return InMemoryRequestRepository()


@pytest.fixture
def notification_repo():
    return InMemoryNotificationRepository()


@pytest.fixture
def refresh_token_repo():
    return InMemoryRefreshTokenRepository()


# ============= User Repository Tests =============

@pytest.mark.asyncio
async def test_user_create_and_get(user_repo):
    """Test creating and retrieving a user"""
    user_id = uuid4()
    user_data = {
        "email": "test@example.com",
        "password_hash": "hashed_password",
        "name": "Test User",
        "phone": "+1234567890"
    }
    
    created = await user_repo.create(user_data)
    assert created.email == "test@example.com"
    
    retrieved = await user_repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.email == "test@example.com"


@pytest.mark.asyncio
async def test_user_get_by_email(user_repo):
    """Test getting user by email"""
    user_data = {
        "email": "findme@example.com",
        "password_hash": "hashed",
        "name": "Find Me",
        "phone": "+1234567890"
    }
    
    await user_repo.create(user_data)
    found = await user_repo.get_by_email("findme@example.com")
    assert found is not None
    assert found.name == "Find Me"


@pytest.mark.asyncio
async def test_user_update(user_repo):
    """Test updating a user"""
    created = await user_repo.create({
        "email": "old@example.com",
        "password_hash": "hash",
        "name": "Old Name",
        "phone": "+1234567890"
    })
    
    updated = await user_repo.update(created.id, {"name": "New Name"})
    assert updated.name == "New Name"


@pytest.mark.asyncio
async def test_user_delete(user_repo):
    """Test deleting a user"""
    created = await user_repo.create({
        "email": "delete@example.com",
        "password_hash": "hash",
        "name": "Delete Me",
        "phone": "+1234567890"
    })
    
    result = await user_repo.delete(created.id)
    assert result is True
    
    found = await user_repo.get_by_id(created.id)
    assert found is None


# ============= Trip Repository Tests =============

@pytest.mark.asyncio
async def test_trip_create_and_get(trip_repo):
    """Test creating and retrieving a trip"""
    driver_id = uuid4()
    trip_data = {
        "driver_id": driver_id,
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 3,
        "price_per_seat": 1500
    }
    
    created = await trip_repo.create(trip_data)
    assert created.from_city == "Moscow"
    assert created.available_seats == 3
    
    retrieved = await trip_repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.to_city == "Saint Petersburg"


@pytest.mark.asyncio
async def test_trip_search(trip_repo):
    """Test searching trips"""
    driver_id = uuid4()
    
    # Create trips
    await trip_repo.create({
        "driver_id": driver_id,
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 3,
        "price_per_seat": 1500
    })
    
    await trip_repo.create({
        "driver_id": driver_id,
        "from_city": "Moscow",
        "to_city": "Kazan",
        "departure_date": "2024-12-26",
        "departure_time": "08:00",
        "available_seats": 2,
        "price_per_seat": 2000
    })
    
    results = await trip_repo.search("Moscow", "Saint Petersburg")
    assert len(results) == 1
    assert results[0].to_city == "Saint Petersburg"


@pytest.mark.asyncio
async def test_trip_update_seats(trip_repo):
    """Test updating available seats"""
    created = await trip_repo.create({
        "driver_id": uuid4(),
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 3,
        "price_per_seat": 1500
    })
    
    # Decrease seats by 1
    updated = await trip_repo.update_seats(created.id, -1)
    assert updated.available_seats == 2
    
    # Increase seats by 1
    updated = await trip_repo.update_seats(created.id, 1)
    assert updated.available_seats == 3


@pytest.mark.asyncio
async def test_trip_update_seats_not_enough(trip_repo):
    """Test that updating seats fails when not enough available"""
    created = await trip_repo.create({
        "driver_id": uuid4(),
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 1,
        "price_per_seat": 1500
    })
    
    with pytest.raises(ValueError, match="Not enough available seats"):
        await trip_repo.update_seats(created.id, -2)


@pytest.mark.asyncio
async def test_trip_delete(trip_repo):
    """Test deleting a trip"""
    created = await trip_repo.create({
        "driver_id": uuid4(),
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 3,
        "price_per_seat": 1500
    })
    
    result = await trip_repo.delete(created.id)
    assert result is True
    
    found = await trip_repo.get_by_id(created.id)
    assert found is None


# ============= Request Repository Tests =============

@pytest.mark.asyncio
async def test_request_create_and_get(request_repo):
    """Test creating and retrieving a request"""
    trip_id = uuid4()
    passenger_id = uuid4()
    
    request_data = {
        "trip_id": trip_id,
        "passenger_id": passenger_id,
        "seats": 2,
        "status": "pending",
        "message": "Please take me"
    }
    
    created = await request_repo.create(request_data)
    assert created.seats_requested == 2
    assert created.status == "pending"
    
    retrieved = await request_repo.get_by_id(created.id)
    assert retrieved is not None
    assert retrieved.message == "Please take me"


@pytest.mark.asyncio
async def test_request_update_status(request_repo):
    """Test updating request status"""
    created = await request_repo.create({
        "trip_id": uuid4(),
        "passenger_id": uuid4(),
        "seats": 1,
        "status": "pending"
    })
    
    updated = await request_repo.update_status(created.id, "confirmed")
    assert updated.status == "confirmed"


@pytest.mark.asyncio
async def test_request_get_by_trip(request_repo):
    """Test getting requests by trip"""
    trip_id = uuid4()
    
    await request_repo.create({
        "trip_id": trip_id,
        "passenger_id": uuid4(),
        "seats": 1,
        "status": "pending"
    })
    
    await request_repo.create({
        "trip_id": trip_id,
        "passenger_id": uuid4(),
        "seats": 2,
        "status": "pending"
    })
    
    results = await request_repo.list_by_trip(trip_id)
    assert len(results) == 2


# ============= Notification Repository Tests =============

@pytest.mark.asyncio
async def test_notification_create_and_get(notification_repo):
    """Test creating and retrieving a notification"""
    user_id = uuid4()
    
    notification_data = {
        "user_id": user_id,
        "title": "Trip Confirmed",
        "message": "Your trip request was confirmed",
        "type": "success"
    }
    
    created = await notification_repo.create(notification_data)
    assert created.title == "Trip Confirmed"
    
    retrieved = await notification_repo.get_by_id(created.id)
    assert retrieved is not None


@pytest.mark.asyncio
async def test_notification_mark_as_read(notification_repo):
    """Test marking notification as read"""
    created = await notification_repo.create({
        "user_id": uuid4(),
        "title": "Test",
        "message": "Test message"
    })
    
    assert created.is_read is False
    
    updated = await notification_repo.mark_read(created.id)
    assert updated.is_read is True


@pytest.mark.asyncio
async def test_notification_get_unread_count(notification_repo):
    """Test getting unread notification count"""
    user_id = uuid4()
    
    await notification_repo.create({
        "user_id": user_id,
        "title": "Notification 1",
        "message": "Message 1"
    })
    
    await notification_repo.create({
        "user_id": user_id,
        "title": "Notification 2",
        "message": "Message 2"
    })
    
    count = await notification_repo.get_unread_count(user_id)
    assert count == 2


# ============= RefreshToken Repository Tests =============

@pytest.mark.asyncio
async def test_refresh_token_create_and_get(refresh_token_repo):
    """Test creating and retrieving a refresh token"""
    user_id = uuid4()
    
    token_data = {
        "user_id": user_id,
        "token": "test_refresh_token_123",
        "expires_in_days": 7
    }
    
    created = await refresh_token_repo.create(token_data)
    assert created.user_id == user_id
    
    retrieved = await refresh_token_repo.get_by_token("test_refresh_token_123")
    assert retrieved is not None


@pytest.mark.asyncio
async def test_refresh_token_revoke(refresh_token_repo):
    """Test revoking a refresh token"""
    created = await refresh_token_repo.create({
        "user_id": uuid4(),
        "token": "token_to_revoke",
        "expires_in_days": 7
    })
    
    result = await refresh_token_repo.revoke("token_to_revoke")
    assert result is True
    
    retrieved = await refresh_token_repo.get_by_token("token_to_revoke")
    assert retrieved.is_revoked is True


@pytest.mark.asyncio
async def test_refresh_token_cleanup_expired(refresh_token_repo):
    """Test cleaning up expired tokens"""
    # Create token and manually set it as expired for testing
    # Note: In real implementation, cleanup happens based on expires_at
    await refresh_token_repo.create({
        "user_id": uuid4(),
        "token": "valid_token",
        "expires_in_days": 7
    })
    
    # Note: The cleanup would remove tokens where expires_at < now
    # This is a basic test to ensure the method exists and runs
    cleaned = await refresh_token_repo.delete_expired()
    assert isinstance(cleaned, int)
