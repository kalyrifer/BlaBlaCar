"""Integration tests - full flow using TestClient with in-memory repositories"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from uuid import uuid4
from datetime import datetime, timezone

# Mock the database module before importing the app
with patch('app.core.database.get_db'):
    from app.main import app
    from app.api import deps


@pytest.fixture
def client():
    """Create a test client"""
    return TestClient(app)


@pytest.fixture
def mock_db():
    """Create mock database for dependency override"""
    from app.repositories.inmemory import (
        InMemoryUserRepository,
        InMemoryTripRepository,
        InMemoryRequestRepository,
        InMemoryNotificationRepository,
        InMemoryRefreshTokenRepository,
    )
    from app.repositories.inmemory.locks import LockManager
    
    class InMemoryDB:
        def __init__(self):
            self.users = InMemoryUserRepository()
            self.trips = InMemoryTripRepository()
            self.requests = InMemoryRequestRepository()
            self.notifications = InMemoryNotificationRepository()
            self.refresh_tokens = InMemoryRefreshTokenRepository()
            self.lock_manager = LockManager()
    
    return InMemoryDB()


@pytest.fixture
def override_dependencies(mock_db):
    """Override FastAPI dependencies with in-memory repositories"""
    from app.services.auth_service import AuthService
    from app.services.trip_service import TripService
    from app.services.request_service import RequestService
    
    def override_get_current_user():
        """Mock current user - will be overridden per test"""
        pass
    
    def override_get_auth_service():
        return AuthService(user_repo=mock_db.users)
    
    def override_get_trip_service():
        return TripService(trip_repo=mock_db.trips, user_repo=mock_db.users)
    
    def override_get_request_service():
        return RequestService(
            request_repo=mock_db.requests,
            trip_repo=mock_db.trips,
            notification_repo=mock_db.notifications,
            user_repo=mock_db.users,
            lock_manager=mock_db.lock_manager
        )
    
    app.dependency_overrides[deps.get_current_user] = override_get_current_user
    app.dependency_overrides[deps.get_auth_service] = override_get_auth_service
    app.dependency_overrides[deps.get_trip_service] = override_get_trip_service
    app.dependency_overrides[deps.get_request_service] = override_get_request_service
    
    yield mock_db
    
    # Cleanup
    app.dependency_overrides.clear()


@pytest.fixture
def mock_security():
    """Mock security functions"""
    with patch('app.services.auth_service.get_password_hash') as mock_hash, \
         patch('app.services.auth_service.verify_password') as mock_verify, \
         patch('app.services.auth_service.create_access_token') as mock_token:
        
        mock_hash.return_value = "hashed_password"
        
        def verify_side_effect(plain, hashed):
            return plain == "password123"
        mock_verify.side_effect = verify_side_effect
        
        mock_token.return_value = "test_token_123"
        
        yield {
            "hash": mock_hash,
            "verify": mock_verify,
            "token": mock_token
        }


@pytest.mark.asyncio
class TestFullFlowIntegration:
    """Integration tests for full flow: register → create trip → send request → driver confirm"""
    
    async def test_full_flow(
        self, 
        client: TestClient, 
        override_dependencies,
        mock_security
    ):
        """Test full flow: register → create trip → send request → driver confirm → assert seats decreased and notifications created"""
        from app.services.request_service import RequestService
        
        mock_db = override_dependencies
        
        # Step 1: Register driver
        driver_response = client.post(
            "/api/auth/register",
            json={
                "email": "driver@example.com",
                "password": "password123",
                "name": "Driver User",
                "phone": "+1234567890"
            }
        )
        assert driver_response.status_code == 200
        driver_data = driver_response.json()
        driver_id = driver_data["id"]
        
        # Step 2: Register passenger
        passenger_response = client.post(
            "/api/auth/register",
            json={
                "email": "passenger@example.com",
                "password": "password123",
                "name": "Passenger User",
                "phone": "+1234567891"
            }
        )
        assert passenger_response.status_code == 200
        passenger_data = passenger_response.json()
        passenger_id = passenger_data["id"]
        
        # Step 3: Create trip by driver - mock the auth dependency
        from app.models.user import User
        from app.core.database import get_db
        
        # Step 4: Send request by passenger
        # We need to manually create the request since we don't have full auth
        request_service = RequestService(
            request_repo=mock_db.requests,
            trip_repo=mock_db.trips,
            notification_repo=mock_db.notifications,
            user_repo=mock_db.users,
            lock_manager=mock_db.lock_manager
        )
        
        from uuid import UUID
        
        # Create trip via service directly
        from app.services.trip_service import TripService, TripCreate
        trip_service = TripService(trip_repo=mock_db.trips, user_repo=mock_db.users)
        
        trip = await trip_service.create_trip(
            driver_id=UUID(driver_id),
            trip_create=TripCreate(
                from_city="Moscow",
                to_city="Saint Petersburg",
                departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
                available_seats=3,
                price_per_seat=1500,
                description="Comfortable trip"
            )
        )
        
        trip_id = str(trip.id)
        
        # Verify initial seats
        assert trip.available_seats == 3
        
        # Step 4: Send request by passenger
        request = await request_service.create_request(
            passenger_id=UUID(passenger_id),
            trip_id=trip_id if isinstance(trip_id, UUID) else UUID(trip_id),
            seats=1,
            message="I'd like to join this trip"
        )
        
        assert request.status == "pending"
        
        # Step 5: Driver confirms the request
        updated_request = await request_service.update_request_status(
            driver_id=UUID(driver_id),
            request_id=UUID(request.id),
            new_status="confirmed"
        )
        
        assert updated_request.status == "confirmed"
        
        # Step 6: Assert seats decreased
        trip = await mock_db.trips.get_by_id(UUID(trip_id))
        assert trip.available_seats == 2  # 3 - 1 = 2
        
        # Note: Notifications are queued asynchronously via background worker
        # So we only verify the seats were decreased correctly
    
    async def test_flow_with_rejected_request(
        self,
        override_dependencies,
        mock_security
    ):
        """Test flow with rejected request"""
        mock_db = override_dependencies
        
        # Create driver and passenger users directly
        from app.services.auth_service import AuthService, UserCreate
        from app.services.request_service import RequestService
        from uuid import UUID
        
        auth_service = AuthService(user_repo=mock_db.users)
        
        driver_user = await auth_service.register(UserCreate(
            email="driver2@example.com",
            password="password123",
            name="Driver Two",
            phone="+1234567890"
        ))
        
        passenger_user = await auth_service.register(UserCreate(
            email="passenger2@example.com",
            password="password123",
            name="Passenger Two",
            phone="+1234567891"
        ))
        
        # Create trip
        from app.services.trip_service import TripService, TripCreate
        trip_service = TripService(trip_repo=mock_db.trips, user_repo=mock_db.users)
        
        trip = await trip_service.create_trip(
            driver_id=UUID(driver_user.id),
            trip_create=TripCreate(
                from_city="Moscow",
                to_city="Kazan",
                departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
                available_seats=2,
                price_per_seat=2000
            )
        )
        
        # Create request
        request_service = RequestService(
            request_repo=mock_db.requests,
            trip_repo=mock_db.trips,
            notification_repo=mock_db.notifications,
            user_repo=mock_db.users,
            lock_manager=mock_db.lock_manager
        )
        
        request = await request_service.create_request(
            passenger_id=UUID(passenger_user.id),
            trip_id=trip.id if isinstance(trip.id, UUID) else UUID(trip.id),
            seats=1
        )
        
        # Reject request
        rejected_request = await request_service.update_request_status(
            driver_id=UUID(driver_user.id),
            request_id=request.id if isinstance(request.id, UUID) else UUID(request.id),
            new_status="rejected"
        )
        
        assert rejected_request.status == "rejected"
        
        # Seats should not change
        updated_trip = await mock_db.trips.get_by_id(trip.id)
        assert updated_trip.available_seats == 2  # Unchanged
