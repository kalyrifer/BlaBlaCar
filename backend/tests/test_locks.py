"""Test demonstrating parallel confirm requests with locking prevents seats going below 0"""
import pytest
import asyncio
from uuid import uuid4

from app.repositories.inmemory import InMemoryTripRepository, InMemoryRequestRepository


@pytest.mark.asyncio
async def test_parallel_confirm_requests_seat_limit():
    """
    Test that parallel confirm requests don't decrease seats below 0.
    
    This test creates a trip with only 1 available seat, then attempts to
    confirm 3 different requests simultaneously. Only 1 should succeed,
    and the other 2 should fail with NotEnoughSeats error.
    """
    trip_repo = InMemoryTripRepository()
    request_repo = InMemoryRequestRepository()
    
    driver_id = uuid4()
    passenger_ids = [uuid4(), uuid4(), uuid4()]
    
    # Create trip with only 1 seat
    trip = await trip_repo.create({
        "driver_id": driver_id,
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 1,  # Only 1 seat!
        "price_per_seat": 1500
    })
    
    # Create 3 pending requests (more than available seats)
    requests = []
    for passenger_id in passenger_ids:
        req = await request_repo.create({
            "trip_id": trip.id,
            "passenger_id": passenger_id,
            "seats_requested": 1,
            "status": "pending"
        })
        requests.append(req)
    
    # Define confirm function that simulates what RequestService does
    async def confirm_request(request_id, seats: int):
        """Attempt to confirm a request with seat reservation"""
        try:
            # Get the request
            trip_request = await request_repo.get_by_id(request_id)
            if not trip_request:
                return {"success": False, "error": "Request not found"}
            
            if trip_request.status != "pending":
                return {"success": False, "error": "Request not pending"}
            
            # Try to reserve seats atomically
            try:
                updated_trip = await trip_repo.update_seats(trip.id, -seats)
            except ValueError as e:
                return {"success": False, "error": str(e)}
            
            # If seats reserved successfully, update request status
            await request_repo.update_status(request_id, "confirmed")
            
            return {"success": True, "seats_remaining": updated_trip.available_seats}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Run confirmations in parallel
    tasks = [
        confirm_request(requests[0].id, 1),
        confirm_request(requests[1].id, 1),
        confirm_request(requests[2].id, 1),
    ]
    
    results = await asyncio.gather(*tasks)
    
    # Count successes and failures
    successes = [r for r in results if r.get("success")]
    failures = [r for r in results if not r.get("success")]
    
    # Only 1 should succeed (we only had 1 seat)
    assert len(successes) == 1, f"Expected 1 success, got {len(successes)}"
    
    # 2 should fail with not enough seats
    assert len(failures) == 2, f"Expected 2 failures, got {len(failures)}"
    
    # Check that seats never went below 0
    final_trip = await trip_repo.get_by_id(trip.id)
    assert final_trip.available_seats >= 0, "Seats went below 0!"
    
    # Final seats should be 0 (1 seat used)
    assert final_trip.available_seats == 0, f"Expected 0 seats remaining, got {final_trip.available_seats}"


@pytest.mark.asyncio
async def test_lock_prevents_race_condition():
    """
    Test that the lock mechanism properly prevents race conditions
    by ensuring sequential execution of seat updates.
    """
    trip_repo = InMemoryTripRepository()
    
    # Create trip with 10 seats
    trip = await trip_repo.create({
        "driver_id": uuid4(),
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 10,
        "price_per_seat": 1500
    })
    
    async def decrement_seats(amount: int):
        """Decrement seats"""
        try:
            # This should be atomic
            updated = await trip_repo.update_seats(trip.id, -amount)
            return updated.available_seats
        except ValueError:
            # When seats run out, it will raise ValueError
            return None
    
    # Run multiple concurrent operations
    results = await asyncio.gather(
        decrement_seats(3),
        decrement_seats(3),
        decrement_seats(3),
        decrement_seats(3),
    )
    
    # Count successful decrements
    successful = [r for r in results if r is not None]
    failed = [r for r in results if r is None]
    
    # Some should succeed, some should fail
    assert len(successful) >= 1, "At least one should succeed"
    assert len(failed) >= 1, "At least one should fail when seats run out"
    
    # Final seats should never go below 0
    final_trip = await trip_repo.get_by_id(trip.id)
    assert final_trip.available_seats >= 0, "Seats went below 0!"


@pytest.mark.asyncio
async def test_lock_allows_concurrent_different_trips():
    """
    Test that locks don't block operations on different trips.
    """
    trip_repo = InMemoryTripRepository()
    
    # Create two different trips
    trip1 = await trip_repo.create({
        "driver_id": uuid4(),
        "from_city": "Moscow",
        "to_city": "Saint Petersburg",
        "departure_date": "2024-12-25",
        "departure_time": "10:00",
        "available_seats": 5,
        "price_per_seat": 1500
    })
    
    trip2 = await trip_repo.create({
        "driver_id": uuid4(),
        "from_city": "Kazan",
        "to_city": "Sochi",
        "departure_date": "2024-12-26",
        "departure_time": "08:00",
        "available_seats": 3,
        "price_per_seat": 2000
    })
    
    # Define operations for different trips
    async def ops_for_trip1():
        for _ in range(3):
            await trip_repo.update_seats(trip1.id, -1)
    
    async def ops_for_trip2():
        for _ in range(2):
            await trip_repo.update_seats(trip2.id, -1)
    
    # Run both concurrently - they should not block each other
    await asyncio.gather(
        ops_for_trip1(),
        ops_for_trip2()
    )
    
    # Both trips should have their seats reduced independently
    final_trip1 = await trip_repo.get_by_id(trip1.id)
    final_trip2 = await trip_repo.get_by_id(trip2.id)
    
    assert final_trip1.available_seats == 2  # 5 - 3 = 2
    assert final_trip2.available_seats == 1  # 3 - 2 = 1
