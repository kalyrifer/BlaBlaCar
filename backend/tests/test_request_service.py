"""Тесты для RequestService"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from app.services.request_service import (
    RequestService, RequestNotFoundError, TripNotFoundError, 
    ForbiddenError, NotEnoughSeatsError, RequestAlreadyExistsError
)
from app.models.request import RequestStatus


# Mock User Repository
class MockUserRepository:
    def __init__(self):
        self.users = {}
    
    async def create(self, user_data: dict):
        from app.models.user import User
        user = User(
            id=user_data.get("id", UUID("12345678-1234-5678-1234-567812345678")),
            email=user_data["email"],
            password_hash=user_data.get("password_hash", ""),
            name=user_data["name"],
            phone=user_data.get("phone", "+1234567890"),
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
        pass
    
    async def delete(self, trip_id: UUID) -> bool:
        return True
    
    async def list_by_filters(self, from_city: str, to_city: str, date: Optional[str] = None, status: str = "active") -> List:
        return []
    
    async def list_by_driver(self, driver_id: UUID) -> List:
        return []
    
    async def update_seats(self, trip_id: UUID, seats_delta: int):
        trip = self.trips.get(trip_id)
        if trip:
            trip.available_seats += seats_delta
        return trip


# Mock Request Repository
class MockRequestRepository:
    def __init__(self):
        self.requests = {}
        self.next_id = 1
    
    async def create(self, request_data: dict):
        from app.models.request import TripRequest
        request_id = UUID(f"32345678-1234-5678-1234-{str(self.next_id).zfill(12)}")
        self.next_id += 1
        request = TripRequest(
            id=request_id,
            trip_id=request_data["trip_id"],
            passenger_id=request_data["passenger_id"],
            seats_requested=request_data["seats_requested"],
            message=request_data.get("message"),
            status=request_data.get("status", "pending"),
            created_at=datetime.now(),
            updated_at=None
        )
        self.requests[request.id] = request
        return request
    
    async def get_by_id(self, request_id: UUID):
        return self.requests.get(request_id)
    
    async def get_by_trip(self, trip_id: UUID):
        return [r for r in self.requests.values() if r.trip_id == trip_id]
    
    async def get_by_passenger(self, passenger_id: UUID):
        return [r for r in self.requests.values() if r.passenger_id == passenger_id]
    
    async def update_status(self, request_id: UUID, status: str):
        request = self.requests.get(request_id)
        if request:
            request.status = status
            request.updated_at = datetime.now()
        return request
    
    async def exists(self, trip_id: UUID, passenger_id: UUID) -> bool:
        for r in self.requests.values():
            if r.trip_id == trip_id and r.passenger_id == passenger_id:
                return True
        return False


# Mock Notification Repository
class MockNotificationRepository:
    def __init__(self):
        self.notifications = {}
    
    async def create(self, notification_data: dict):
        from app.models.notification import Notification
        notification = Notification(
            id=UUID("42345678-1234-5678-1234-567812345678"),
            user_id=notification_data["user_id"],
            type=notification_data["type"],
            title=notification_data["title"],
            message=notification_data["message"],
            related_trip_id=notification_data.get("related_trip_id"),
            related_request_id=notification_data.get("related_request_id"),
            is_read=False,
            created_at=datetime.now()
        )
        self.notifications[notification.id] = notification
        return notification
    
    async def get_by_id(self, notification_id: UUID):
        return self.notifications.get(notification_id)
    
    async def get_by_user(self, user_id: UUID, is_read: Optional[bool] = None):
        pass
    
    async def mark_as_read(self, notification_id: UUID):
        pass
    
    async def mark_all_as_read(self, user_id: UUID):
        pass
    
    async def get_unread_count(self, user_id: UUID):
        pass


@pytest.mark.asyncio
class TestRequestService:
    
    async def test_create_request_success(self):
        """Тест успешного создания заявки"""
        user_repo = MockUserRepository()
        trip_repo = MockTripRepository()
        request_repo = MockRequestRepository()
        notification_repo = MockNotificationRepository()
        
        # Создаем пользователей
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        passenger_id = UUID("22345678-1234-5678-1234-567812345678")
        
        await user_repo.create({
            "id": driver_id,
            "email": "driver@example.com",
            "name": "Driver User",
            "phone": "+1234567890"
        })
        await user_repo.create({
            "id": passenger_id,
            "email": "passenger@example.com",
            "name": "Passenger User",
            "phone": "+0987654321"
        })
        
        # Создаем поездку
        trip = await trip_repo.create({
            "driver_id": driver_id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_date": "2024-06-01",
            "departure_time": "10:00",
            "available_seats": 3,
            "price_per_seat": 1500
        })
        
        request_service = RequestService(
            request_repo, trip_repo, notification_repo, user_repo
        )
        
        result = await request_service.create_request(
            passenger_id=passenger_id,
            trip_id=trip.id,
            seats=1,
            message="Please take me"
        )
        
        assert result.passenger_id == str(passenger_id)
        assert result.seats_requested == 1
        assert result.status == "pending"
    
    async def test_create_request_own_trip(self):
        """Тест создания заявки на свою собственную поездку"""
        user_repo = MockUserRepository()
        trip_repo = MockTripRepository()
        request_repo = MockRequestRepository()
        notification_repo = MockNotificationRepository()
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        
        await user_repo.create({
            "id": driver_id,
            "email": "driver@example.com",
            "name": "Driver User",
            "phone": "+1234567890"
        })
        
        trip = await trip_repo.create({
            "driver_id": driver_id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_date": "2024-06-01",
            "departure_time": "10:00",
            "available_seats": 3,
            "price_per_seat": 1500
        })
        
        request_service = RequestService(
            request_repo, trip_repo, notification_repo, user_repo
        )
        
        with pytest.raises(ValueError, match="Cannot request your own trip"):
            await request_service.create_request(
                passenger_id=driver_id,
                trip_id=trip.id,
                seats=1
            )
    
    async def test_create_request_not_enough_seats(self):
        """Тест создания заявки при недостатке мест"""
        user_repo = MockUserRepository()
        trip_repo = MockTripRepository()
        request_repo = MockRequestRepository()
        notification_repo = MockNotificationRepository()
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        passenger_id = UUID("22345678-1234-5678-1234-567812345678")
        
        await user_repo.create({
            "id": driver_id,
            "email": "driver@example.com",
            "name": "Driver User",
            "phone": "+1234567890"
        })
        await user_repo.create({
            "id": passenger_id,
            "email": "passenger@example.com",
            "name": "Passenger User",
            "phone": "+0987654321"
        })
        
        trip = await trip_repo.create({
            "driver_id": driver_id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_date": "2024-06-01",
            "departure_time": "10:00",
            "available_seats": 1,
            "price_per_seat": 1500
        })
        
        request_service = RequestService(
            request_repo, trip_repo, notification_repo, user_repo
        )
        
        with pytest.raises(NotEnoughSeatsError, match="Not enough available seats"):
            await request_service.create_request(
                passenger_id=passenger_id,
                trip_id=trip.id,
                seats=5  # Запрашиваем больше, чем доступно
            )
    
    async def test_update_request_status_confirm(self):
        """Тест подтверждения заявки"""
        user_repo = MockUserRepository()
        trip_repo = MockTripRepository()
        request_repo = MockRequestRepository()
        notification_repo = MockNotificationRepository()
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        passenger_id = UUID("22345678-1234-5678-1234-567812345678")
        
        await user_repo.create({
            "id": driver_id,
            "email": "driver@example.com",
            "name": "Driver User",
            "phone": "+1234567890"
        })
        await user_repo.create({
            "id": passenger_id,
            "email": "passenger@example.com",
            "name": "Passenger User",
            "phone": "+0987654321"
        })
        
        trip = await trip_repo.create({
            "driver_id": driver_id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_date": "2024-06-01",
            "departure_time": "10:00",
            "available_seats": 3,
            "price_per_seat": 1500
        })
        
        # Создаем заявку
        request = await request_repo.create({
            "trip_id": trip.id,
            "passenger_id": passenger_id,
            "seats_requested": 2,
            "message": "I want to go",
            "status": "pending"
        })
        
        request_service = RequestService(
            request_repo, trip_repo, notification_repo, user_repo
        )
        
        result = await request_service.update_request_status(
            driver_id=driver_id,
            request_id=request.id,
            new_status=RequestStatus.CONFIRMED
        )
        
        assert result.status == "confirmed"
        
        # Проверяем, что места уменьшились
        updated_trip = await trip_repo.get_by_id(trip.id)
        assert updated_trip.available_seats == 1  # 3 - 2 = 1
    
    async def test_update_request_status_not_owner(self):
        """Тест обновления статуса не владельцем поездки"""
        user_repo = MockUserRepository()
        trip_repo = MockTripRepository()
        request_repo = MockRequestRepository()
        notification_repo = MockNotificationRepository()
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        other_driver_id = UUID("32345678-1234-5678-1234-567812345678")
        passenger_id = UUID("22345678-1234-5678-1234-567812345678")
        
        await user_repo.create({
            "id": driver_id,
            "email": "driver@example.com",
            "name": "Driver User",
            "phone": "+1234567890"
        })
        await user_repo.create({
            "id": passenger_id,
            "email": "passenger@example.com",
            "name": "Passenger User",
            "phone": "+0987654321"
        })
        
        trip = await trip_repo.create({
            "driver_id": driver_id,
            "from_city": "Moscow",
            "to_city": "Saint Petersburg",
            "departure_date": "2024-06-01",
            "departure_time": "10:00",
            "available_seats": 3,
            "price_per_seat": 1500
        })
        
        request = await request_repo.create({
            "trip_id": trip.id,
            "passenger_id": passenger_id,
            "seats_requested": 1,
            "message": "I want to go",
            "status": "pending"
        })
        
        request_service = RequestService(
            request_repo, trip_repo, notification_repo, user_repo
        )
        
        with pytest.raises(ForbiddenError, match="Not authorized to update this request"):
            await request_service.update_request_status(
                driver_id=other_driver_id,  # Другой пользователь
                request_id=request.id,
                new_status=RequestStatus.CONFIRMED
            )
    
    async def test_update_request_not_found(self):
        """Тест обновления несуществующей заявки"""
        user_repo = MockUserRepository()
        trip_repo = MockTripRepository()
        request_repo = MockRequestRepository()
        notification_repo = MockNotificationRepository()
        
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        
        request_service = RequestService(
            request_repo, trip_repo, notification_repo, user_repo
        )
        
        nonexistent_request_id = UUID("52345678-1234-5678-1234-567812345678")
        
        with pytest.raises(RequestNotFoundError, match="Request not found"):
            await request_service.update_request_status(
                driver_id=driver_id,
                request_id=nonexistent_request_id,
                new_status=RequestStatus.CONFIRMED
            )