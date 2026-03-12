"""Тесты для TripService"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from app.services.trip_service import (
    TripService, TripCreate, TripSearchFilters, 
    TripNotFoundError, ForbiddenError
)


# Mock User Repository
class MockUserRepository:
    def __init__(self):
        self.users = {}
    
    async def create(self, user_data: dict):
        from app.models.user import User
        user = User(
            id=UUID("12345678-1234-5678-1234-567812345678"),
            email=user_data["email"],
            password_hash=user_data.get("password_hash", ""),
            name=user_data["name"],
            phone=user_data.get("phone"),
            avatar_url=None,
            rating=4.5,
            created_at=datetime.now()
        )
        self.users[user.id] = user
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional["User"]:
        return self.users.get(user_id)
    
    async def get_by_email(self, email: str):
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    async def update(self, user_id: UUID, user_data: dict):
        pass
    
    async def delete(self, user_id: UUID) -> bool:
        return True
    
    async def list_all(self):
        return list(self.users.values())


# Mock Trip Repository
class MockTripRepository:
    def __init__(self):
        self.trips = {}
    
    async def create(self, trip_data: dict):
        from app.models.trip import Trip
        trip_id = UUID("22345678-1234-5678-1234-567812345678")
        trip = Trip(
            id=trip_id,
            driver_id=trip_data["driver_id"],
            from_city=trip_data["from_city"],
            to_city=trip_data["to_city"],
            departure_date=trip_data["departure_date"],
            departure_time=trip_data["departure_time"],
            available_seats=trip_data["available_seats"],
            price_per_seat=trip_data["price_per_seat"],
            description=trip_data.get("description"),
            status=trip_data.get("status", "active"),
            created_at=datetime.now()
        )
        self.trips[trip.id] = trip
        return trip
    
    async def get_by_id(self, trip_id: UUID):
        return self.trips.get(trip_id)
    
    async def update(self, trip_id: UUID, trip_data: dict):
        trip = self.trips.get(trip_id)
        if trip:
            for key, value in trip_data.items():
                setattr(trip, key, value)
        return trip
    
    async def delete(self, trip_id: UUID) -> bool:
        if trip_id in self.trips:
            del self.trips[trip_id]
            return True
        return False
    
    async def list_by_filters(self, from_city: str, to_city: str, date: Optional[str] = None, status: str = "active") -> List["Trip"]:
        results = []
        for trip in self.trips.values():
            if trip.from_city == from_city and trip.to_city == to_city:
                if date is None or trip.departure_date == date:
                    if trip.status == status:
                        results.append(trip)
        return results
    
    async def list_by_driver(self, driver_id: UUID) -> List["Trip"]:
        return [trip for trip in self.trips.values() if trip.driver_id == driver_id]
    
    async def update_seats(self, trip_id: UUID, seats_delta: int):
        trip = self.trips.get(trip_id)
        if trip:
            trip.available_seats += seats_delta
        return trip


@pytest.mark.asyncio
class TestTripService:
    
    async def test_create_trip_success(self):
        """Тест успешного создания поездки"""
        trip_repo = MockTripRepository()
        user_repo = MockUserRepository()
        trip_service = TripService(trip_repo, user_repo)
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_at="2024-06-01T10:00:00",
            available_seats=3,
            price_per_seat=1500,
            description="Comfortable trip"
        )
        
        result = await trip_service.create_trip(driver_id, trip_create)
        
        assert result.from_city == "Moscow"
        assert result.to_city == "Saint Petersburg"
        assert result.available_seats == 3
        assert result.price_per_seat == 1500
        assert result.status == "active"
    
    async def test_search_trips_success(self):
        """Тест успешного поиска поездок"""
        trip_repo = MockTripRepository()
        user_repo = MockUserRepository()
        trip_service = TripService(trip_repo, user_repo)
        
        # Создаем тестовую поездку
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_date="2024-06-01",
            departure_time="10:00",
            available_seats=3,
            price_per_seat=1500
        )
        await trip_service.create_trip(driver_id, trip_create)
        
        # Ищем поездки
        filters = TripSearchFilters(
            from_city="Moscow",
            to_city="Saint Petersburg"
        )
        
        result = await trip_service.search_trips(filters, page=1, page_size=20)
        
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0]["from_city"] == "Moscow"
    
    async def test_delete_trip_success(self):
        """Тест успешного удаления поездки владельцем"""
        trip_repo = MockTripRepository()
        user_repo = MockUserRepository()
        trip_service = TripService(trip_repo, user_repo)
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_date="2024-06-01",
            departure_time="10:00",
            available_seats=3,
            price_per_seat=1500
        )
        
        result = await trip_service.create_trip(driver_id, trip_create)
        trip_id = UUID(result.id)
        
        # Удаляем поездку
        await trip_service.delete_or_cancel_trip(driver_id, trip_id)
        
        # Проверяем, что поездка удалена
        assert await trip_repo.get_by_id(trip_id) is None
    
    async def test_delete_trip_not_owner(self):
        """Тест удаления поездки не владельцем"""
        trip_repo = MockTripRepository()
        user_repo = MockUserRepository()
        trip_service = TripService(trip_repo, user_repo)
        
        # Создаем поездку от одного водителя
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_date="2024-06-01",
            departure_time="10:00",
            available_seats=3,
            price_per_seat=1500
        )
        
        result = await trip_service.create_trip(driver_id, trip_create)
        trip_id = UUID(result.id)
        
        # Пытаемся удалить от другого пользователя
        other_driver_id = UUID("32345678-1234-5678-1234-567812345678")
        
        with pytest.raises(ForbiddenError, match="Not the owner of this trip"):
            await trip_service.delete_or_cancel_trip(other_driver_id, trip_id)
    
    async def test_delete_trip_not_found(self):
        """Тест удаления несуществующей поездки"""
        trip_repo = MockTripRepository()
        user_repo = MockUserRepository()
        trip_service = TripService(trip_repo, user_repo)
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        nonexistent_trip_id = UUID("42345678-1234-5678-1234-567812345678")
        
        with pytest.raises(TripNotFoundError, match="Trip not found"):
            await trip_service.delete_or_cancel_trip(driver_id, nonexistent_trip_id)