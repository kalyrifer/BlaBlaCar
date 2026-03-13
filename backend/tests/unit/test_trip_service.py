"""Unit tests for TripService - create_trip"""
import pytest
from uuid import uuid4
from datetime import datetime, timezone

from app.services.trip_service import TripService, TripCreate, TripSearchFilters
from app.core.exceptions import NotFoundError, ForbiddenError
from app.repositories.inmemory import InMemoryUserRepository, InMemoryTripRepository


@pytest.mark.asyncio
class TestTripServiceCreateTrip:
    """Tests for TripService.create_trip"""
    
    async def test_create_trip_success(self):
        """Test successful trip creation"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        # Create driver first
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            available_seats=3,
            price_per_seat=1500,
            description="Comfortable trip"
        )
        
        result = await trip_service.create_trip(driver.id, trip_create)
        
        assert result.from_city == "Moscow"
        assert result.to_city == "Saint Petersburg"
        assert result.available_seats == 3
        assert result.price_per_seat == 1500
        assert result.status == "active"
        assert str(result.driver_id) == str(driver.id)
    
    async def test_create_trip_with_zero_seats(self):
        """Test trip creation with zero seats"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            available_seats=0,
            price_per_seat=1500
        )
        
        result = await trip_service.create_trip(driver.id, trip_create)
        
        assert result.available_seats == 0
    
    async def test_create_multiple_trips(self):
        """Test creating multiple trips"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        trip1 = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            available_seats=3,
            price_per_seat=1500
        )
        trip2 = TripCreate(
            from_city="Moscow",
            to_city="Kazan",
            departure_at=datetime(2024, 6, 2, 12, 0, 0, tzinfo=timezone.utc),
            available_seats=2,
            price_per_seat=2000
        )
        
        result1 = await trip_service.create_trip(driver.id, trip1)
        result2 = await trip_service.create_trip(driver.id, trip2)
        
        assert result1.id != result2.id
        assert result1.to_city == "Saint Petersburg"
        assert result2.to_city == "Kazan"


@pytest.mark.asyncio
class TestTripServiceSearchTrips:
    """Tests for TripService.search_trips"""
    
    async def test_search_trips_found(self):
        """Test searching for existing trips"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        # Create a trip
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            available_seats=3,
            price_per_seat=1500
        )
        await trip_service.create_trip(driver.id, trip_create)
        
        # Search for trips
        filters = TripSearchFilters(
            from_city="Moscow",
            to_city="Saint Petersburg"
        )
        
        result = await trip_service.search_trips(filters, page=1, page_size=20)
        
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0]["from_city"] == "Moscow"
        assert result.items[0]["to_city"] == "Saint Petersburg"
    
    async def test_search_trips_not_found(self):
        """Test searching for non-existent trips"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        filters = TripSearchFilters(
            from_city="Moscow",
            to_city="NonExistent"
        )
        
        result = await trip_service.search_trips(filters, page=1, page_size=20)
        
        assert result.total == 0
        assert len(result.items) == 0
    
    async def test_search_trips_pagination(self):
        """Test trip search pagination"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        # Create multiple trips
        for i in range(5):
            trip_create = TripCreate(
                from_city="Moscow",
                to_city="Saint Petersburg",  # Same destination for pagination
                departure_at=datetime(2024, 6, i+1, 10, 0, 0, tzinfo=timezone.utc),
                available_seats=3,
                price_per_seat=1500
            )
            await trip_service.create_trip(driver.id, trip_create)
        
        # Search with pagination
        filters = TripSearchFilters(
            from_city="Moscow",
            to_city="Saint Petersburg"
        )
        
        result = await trip_service.search_trips(filters, page=1, page_size=3)
        
        assert result.total == 5
        assert len(result.items) == 3
        assert result.page == 1
        assert result.pages == 2


@pytest.mark.asyncio
class TestTripServiceDeleteTrip:
    """Tests for TripService.delete_or_cancel_trip"""
    
    async def test_delete_trip_success(self):
        """Test successful trip deletion by owner"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        # Create a trip
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            available_seats=3,
            price_per_seat=1500
        )
        result = await trip_service.create_trip(driver.id, trip_create)
        
        # Delete the trip
        from uuid import UUID
        trip_uuid = UUID(result.id) if isinstance(result.id, str) else result.id
        await trip_service.delete_or_cancel_trip(driver.id, trip_uuid)
        
        # Verify deletion
        trip = await trip_repo.get_by_id(trip_uuid)
        assert trip is None
    
    async def test_delete_trip_not_owner(self):
        """Test deleting trip by non-owner fails"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        passenger = await user_repo.create({
            "email": "passenger@example.com",
            "password_hash": "hashed",
            "name": "Passenger",
            "phone": "+1234567891"
        })
        
        # Create a trip by driver
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_at=datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            available_seats=3,
            price_per_seat=1500
        )
        result = await trip_service.create_trip(driver.id, trip_create)
        
        # Try to delete as passenger
        from uuid import UUID
        trip_uuid = UUID(result.id) if isinstance(result.id, str) else result.id
        with pytest.raises(ForbiddenError, match="Not authorized to delete this trip"):
            await trip_service.delete_or_cancel_trip(passenger.id, trip_uuid)
    
    async def test_delete_trip_not_found(self):
        """Test deleting non-existent trip fails"""
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        trip_service = TripService(trip_repo=trip_repo, user_repo=user_repo)
        
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        nonexistent_trip_id = uuid4()
        
        with pytest.raises(NotFoundError, match="Trip not found"):
            await trip_service.delete_or_cancel_trip(driver.id, nonexistent_trip_id)
