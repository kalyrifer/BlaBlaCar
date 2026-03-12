"""Concurrency tests for RequestService"""
import asyncio
import pytest
import pytest_asyncio
from uuid import uuid4
from datetime import datetime

from app.repositories.inmemory import (
    InMemoryUserRepository,
    InMemoryTripRepository,
    InMemoryRequestRepository,
    InMemoryNotificationRepository,
)
from app.repositories.inmemory.locks import LockManager, get_lock_manager
from app.services.request_service import RequestService, NotEnoughSeatsError
from app.models.request import RequestStatus


@pytest.mark.asyncio
async def test_parallel_confirm_only_one_succeeds():
    """
    Test that when 3 parallel confirm requests are made on a trip with 1 seat,
    only 1 confirmation succeeds and the other 2 get NotEnoughSeatsError.
    """
    # Use global lock manager for shared locking
    lock_mgr = get_lock_manager()
    lock_mgr.clear_locks()
    
    # Create repos
    user_repo = InMemoryUserRepository()
    trip_repo = InMemoryTripRepository()
    request_repo = InMemoryRequestRepository()
    notification_repo = InMemoryNotificationRepository()
    
    service = RequestService(
        request_repo=request_repo,
        trip_repo=trip_repo,
        notification_repo=notification_repo,
        user_repo=user_repo,
        lock_manager=lock_mgr
    )
    
    # Create driver
    driver_id = uuid4()
    await user_repo.create({
        "id": driver_id,
        "email": "driver@test.com",
        "name": "Driver",
        "password_hash": "hash",
        "phone": "+79000000000",
        "avatar_url": None,
        "rating": 5.0,
        "created_at": datetime.utcnow()
    })
    
    # Create trip with 1 available seat
    trip_id = uuid4()
    await trip_repo.create({
        "id": trip_id,
        "driver_id": driver_id,
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2025-06-01",
        "departure_time": "10:00",
        "available_seats": 1,
        "price_per_seat": 1000,
        "status": "active",
        "created_at": datetime.utcnow()
    })
    
    # Create 3 passengers with pending requests
    passenger_ids = []
    request_ids = []
    for i in range(3):
        passenger_id = uuid4()
        await user_repo.create({
            "id": passenger_id,
            "email": f"passenger{i}@test.com",
            "name": f"Passenger {i}",
            "password_hash": "hash",
            "phone": f"+7900000000{i}",
            "avatar_url": None,
            "rating": 5.0,
            "created_at": datetime.utcnow()
        })
        
        request_id = uuid4()
        await request_repo.create({
            "id": request_id,
            "trip_id": trip_id,
            "passenger_id": passenger_id,
            "seats_requested": 1,
            "message": f"Request {i}",
            "status": RequestStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": None
        })
        
        passenger_ids.append(passenger_id)
        request_ids.append(request_id)
    
    # Track results
    results = {"success": 0, "failed": 0, "errors": []}
    results_lock = asyncio.Lock()
    
    async def try_confirm(request_id):
        """Try to confirm a request"""
        try:
            await service.update_request_status(
                driver_id=driver_id,
                request_id=request_id,
                new_status=RequestStatus.CONFIRMED
            )
            async with results_lock:
                results["success"] += 1
        except NotEnoughSeatsError as e:
            async with results_lock:
                results["failed"] += 1
                results["errors"].append(str(e))
        except Exception as e:
            async with results_lock:
                results["failed"] += 1
                results["errors"].append(f"{type(e).__name__}: {e}")
    
    # Run all confirmations in parallel
    await asyncio.gather(*[try_confirm(rid) for rid in request_ids])
    
    # Verify: exactly 1 success, 2 failures
    assert results["success"] == 1, f"Expected 1 success, got {results['success']}"
    assert results["failed"] == 2, f"Expected 2 failures, got {results['failed']}"
    
    # All failures should be NotEnoughSeatsError
    for error in results["errors"]:
        assert "Not enough" in error, f"Expected NotEnoughSeatsError, got: {error}"
    
    # Verify final state: trip should have 0 seats
    trip = await trip_repo.get_by_id(trip_id)
    assert trip.available_seats == 0, f"Expected 0 seats, got {trip.available_seats}"


@pytest.mark.asyncio
async def test_parallel_confirm_seats_never_negative():
    """
    Test that seats never go negative even under high concurrency.
    """
    # Use global lock manager
    lock_mgr = get_lock_manager()
    lock_mgr.clear_locks()
    
    # Create repos
    user_repo = InMemoryUserRepository()
    trip_repo = InMemoryTripRepository()
    request_repo = InMemoryRequestRepository()
    notification_repo = InMemoryNotificationRepository()
    
    service = RequestService(
        request_repo=request_repo,
        trip_repo=trip_repo,
        notification_repo=notification_repo,
        user_repo=user_repo,
        lock_manager=lock_mgr
    )
    
    # Create driver
    driver_id = uuid4()
    await user_repo.create({
        "id": driver_id,
        "email": "driver@test.com",
        "name": "Driver",
        "password_hash": "hash",
        "phone": "+79000000000",
        "avatar_url": None,
        "rating": 5.0,
        "created_at": datetime.utcnow()
    })
    
    # Create trip with 1 seat
    trip_id = uuid4()
    await trip_repo.create({
        "id": trip_id,
        "driver_id": driver_id,
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2025-06-01",
        "departure_time": "10:00",
        "available_seats": 1,
        "price_per_seat": 1000,
        "status": "active",
        "created_at": datetime.utcnow()
    })
    
    # Create 3 passengers
    passenger_ids = []
    request_ids = []
    for i in range(3):
        passenger_id = uuid4()
        await user_repo.create({
            "id": passenger_id,
            "email": f"p{i}@test.com",
            "name": f"P{i}",
            "password_hash": "hash",
            "phone": f"+790000000{i}",
            "avatar_url": None,
            "rating": 5.0,
            "created_at": datetime.utcnow()
        })
        
        request_id = uuid4()
        await request_repo.create({
            "id": request_id,
            "trip_id": trip_id,
            "passenger_id": passenger_id,
            "seats_requested": 1,
            "message": f"Request {i}",
            "status": RequestStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": None
        })
        
        passenger_ids.append(passenger_id)
        request_ids.append(request_id)
    
    # Track minimum seats seen
    min_seats_seen = float('inf')
    
    async def try_confirm_with_check(request_id):
        nonlocal min_seats_seen
        try:
            await service.update_request_status(
                driver_id=driver_id,
                request_id=request_id,
                new_status=RequestStatus.CONFIRMED
            )
            trip = await trip_repo.get_by_id(trip_id)
            min_seats_seen = min(min_seats_seen, trip.available_seats)
        except NotEnoughSeatsError:
            pass
    
    # Run in parallel
    await asyncio.gather(*[try_confirm_with_check(rid) for rid in request_ids])
    
    # Seats should never go below 0
    trip = await trip_repo.get_by_id(trip_id)
    assert trip.available_seats >= 0, f"Seats went negative: {trip.available_seats}"
    assert min_seats_seen >= 0, f"Min seats seen was negative: {min_seats_seen}"


@pytest.mark.asyncio
async def test_different_trips_dont_block_each_other():
    """
    Test that locking one trip doesn't block updates to another trip.
    """
    # Use global lock manager for shared locking
    lock_mgr = get_lock_manager()
    lock_mgr.clear_locks()
    
    # Create repos
    user_repo = InMemoryUserRepository()
    trip_repo = InMemoryTripRepository()
    request_repo = InMemoryRequestRepository()
    notification_repo = InMemoryNotificationRepository()
    
    service = RequestService(
        request_repo=request_repo,
        trip_repo=trip_repo,
        notification_repo=notification_repo,
        user_repo=user_repo,
        lock_manager=lock_mgr
    )
    
    driver_id = uuid4()
    
    # Create driver
    await user_repo.create({
        "id": driver_id,
        "email": "driver@test.com",
        "name": "Driver",
        "password_hash": "hash",
        "phone": "+79000000000",
        "avatar_url": None,
        "rating": 5.0,
        "created_at": datetime.utcnow()
    })
    
    # Create trip 1 with 2 seats (can confirm 2 requests)
    trip1_id = uuid4()
    await trip_repo.create({
        "id": trip1_id,
        "driver_id": driver_id,
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2025-06-01",
        "departure_time": "10:00",
        "available_seats": 2,
        "price_per_seat": 1000,
        "status": "active",
        "created_at": datetime.utcnow()
    })
    
    # Create 2 passengers for trip 1
    passenger_ids = []
    request_ids = []
    for i in range(2):
        passenger_id = uuid4()
        await user_repo.create({
            "id": passenger_id,
            "email": f"p{i}@test.com",
            "name": f"P{i}",
            "password_hash": "hash",
            "phone": f"+790000000{i}",
            "avatar_url": None,
            "rating": 5.0,
            "created_at": datetime.utcnow()
        })
        
        request_id = uuid4()
        await request_repo.create({
            "id": request_id,
            "trip_id": trip1_id,
            "passenger_id": passenger_id,
            "seats_requested": 1,
            "message": f"Request {i}",
            "status": RequestStatus.PENDING,
            "created_at": datetime.utcnow(),
            "updated_at": None
        })
        
        passenger_ids.append(passenger_id)
        request_ids.append(request_id)
    
    # Confirm both - both should succeed (2 seats available)
    results = []
    for rid in request_ids:
        result = await service.update_request_status(
            driver_id=driver_id,
            request_id=rid,
            new_status=RequestStatus.CONFIRMED
        )
        results.append(result)
    
    # Both should succeed
    assert len(results) == 2, f"Expected 2 successes, got {len(results)}"
    
    # Trip should have 0 seats
    trip = await trip_repo.get_by_id(trip1_id)
    assert trip.available_seats == 0, f"Expected 0 seats, got {trip.available_seats}"
