"""Concurrency tests - simulate 10 concurrent confirmations for trip with 1 seat; assert only 1 success"""
import pytest
import asyncio
from uuid import uuid4
from datetime import datetime, timezone

from app.repositories.inmemory import (
    InMemoryUserRepository,
    InMemoryTripRepository,
    InMemoryRequestRepository,
    InMemoryNotificationRepository,
)
from app.repositories.inmemory.locks import LockManager
from app.services.request_service import RequestService
from app.services.trip_service import TripService
from app.services.auth_service import AuthService, UserCreate


@pytest.mark.asyncio
class TestRequestConcurrency:
    """Tests for concurrent request confirmation - race condition protection"""
    
    async def test_concurrent_confirmations_one_seat(self):
        """Test that only 1 out of 10 concurrent confirmations succeeds for a trip with 1 seat"""
        # Setup repositories
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        request_repo = InMemoryRequestRepository()
        notification_repo = InMemoryNotificationRepository()
        lock_manager = LockManager()
        
        # Create driver
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        # Create 10 passengers
        passengers = []
        for i in range(10):
            passenger = await user_repo.create({
                "email": f"passenger{i}@example.com",
                "password_hash": "hashed",
                "name": f"Passenger {i}",
                "phone": f"+123456789{i}"
            })
            passengers.append(passenger)
        
        # Create trip with 1 seat
        trip = await trip_repo.create({
            "driver_id": driver.id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_at": datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            "available_seats": 1,  # Only 1 seat!
            "price_per_seat": 1500,
            "status": "active"
        })
        
        # Create 10 pending requests (one per passenger)
        requests = []
        for passenger in passengers:
            request = await request_repo.create({
                "trip_id": trip.id,
                "passenger_id": passenger.id,
                "seats_requested": 1,
                "status": "pending"
            })
            requests.append(request)
        
        # Now try to confirm all 10 requests concurrently
        request_service = RequestService(
            request_repo=request_repo,
            trip_repo=trip_repo,
            notification_repo=notification_repo,
            user_repo=user_repo,
            lock_manager=lock_manager
        )
        
        async def confirm_request(request_id):
            """Try to confirm a request"""
            try:
                result = await request_service.update_request_status(
                    driver_id=driver.id,
                    request_id=request_id,
                    new_status="confirmed"
                )
                return ("success", result)
            except Exception as e:
                return ("error", str(e))
        
        # Run all confirmations concurrently
        results = await asyncio.gather(*[confirm_request(req.id) for req in requests])
        
        # Count successes and errors
        successes = [r for r in results if r[0] == "success"]
        errors = [r for r in results if r[0] == "error"]
        
        # Assert: Only 1 confirmation should succeed
        assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"
        
        # Assert: 9 should fail with "Not enough available seats"
        assert len(errors) == 9, f"Expected 9 errors, got {len(errors)}"
        
        # Verify error messages contain "Not enough"
        error_messages = [e[1] for e in errors]
        assert any("Not enough" in msg for msg in error_messages), "Expected 'Not enough seats' error"
        
        # Verify trip has 0 seats remaining (1 - 1 = 0)
        updated_trip = await trip_repo.get_by_id(trip.id)
        assert updated_trip.available_seats == 0, f"Expected 0 seats, got {updated_trip.available_seats}"
    
    async def test_concurrent_seat_updates(self):
        """Test concurrent seat updates are handled atomically"""
        # Setup
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        lock_manager = LockManager()
        
        # Create driver
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        # Create trip with 5 seats
        trip = await trip_repo.create({
            "driver_id": driver.id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_at": datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            "available_seats": 5,
            "price_per_seat": 1500,
            "status": "active"
        })
        
        # Concurrently decrease seats 5 times (by 1 each)
        async def decrease_seats():
            return await trip_repo.update_seats(trip.id, -1)
        
        results = await asyncio.gather(*[decrease_seats() for _ in range(5)], return_exceptions=True)
        
        # All should succeed
        successes = [r for r in results if not isinstance(r, Exception)]
        exceptions = [r for r in results if isinstance(r, Exception)]
        
        assert len(successes) == 5, f"All seat decreases should succeed, got {len(successes)}"
        assert len(exceptions) == 0, f"No exceptions expected, got {len(exceptions)}"
        
        # Verify final seat count
        updated_trip = await trip_repo.get_by_id(trip.id)
        assert updated_trip.available_seats == 0, f"Expected 0 seats, got {updated_trip.available_seats}"
    
    async def test_concurrent_over_decrease_fails(self):
        """Test that concurrent over-decrease (more than available) fails"""
        # Setup
        user_repo = InMemoryUserRepository()
        trip_repo = InMemoryTripRepository()
        
        # Create driver
        driver = await user_repo.create({
            "email": "driver@example.com",
            "password_hash": "hashed",
            "name": "Driver",
            "phone": "+1234567890"
        })
        
        # Create trip with 3 seats
        trip = await trip_repo.create({
            "driver_id": driver.id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_at": datetime(2024, 6, 1, 10, 0, 0, tzinfo=timezone.utc),
            "available_seats": 3,
            "price_per_seat": 1500,
            "status": "active"
        })
        
        # Try to decrease by 5 (more than available)
        async def decrease_seats(delta):
            try:
                result = await trip_repo.update_seats(trip.id, delta)
                return ("success", result)
            except Exception as e:
                return ("error", str(e))
        
        # Run 5 concurrent decreases of -1 each (total -5)
        results = await asyncio.gather(*[
            decrease_seats(-1) for _ in range(5)
        ])
        
        # Some should succeed, some should fail
        successes = [r for r in results if r[0] == "success"]
        errors = [r for r in results if r[0] == "error"]
        
        # At most 3 should succeed (3 seats)
        assert len(successes) <= 3, f"Max 3 successes expected, got {len(successes)}"
        
        # At least 2 should fail (trying to go below 0)
        assert len(errors) >= 2, f"At least 2 errors expected, got {len(errors)}"
