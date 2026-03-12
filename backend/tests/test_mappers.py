"""Tests for schema <-> ORM mappers"""
import pytest
from datetime import datetime
from uuid import UUID
from unittest.mock import MagicMock

from app.utils import mappers
from app.schemas.user import UserCreate, UserUpdate
from app.schemas.trip import TripCreate, TripUpdate
from app.schemas.request import RequestCreate, RequestStatusUpdate
from app.schemas.notification import NotificationCreate


class TestUserMappers:
    """Tests for User mappers"""
    
    def test_user_orm_to_response(self):
        """Test mapping User ORM to UserResponse"""
        # Create mock ORM object
        mock_user = MagicMock()
        mock_user.id = UUID("12345678-1234-5678-1234-567812345678")
        mock_user.email = "test@example.com"
        mock_user.name = "Test User"
        mock_user.phone = "+1234567890"
        mock_user.avatar_url = "http://example.com/avatar.jpg"
        mock_user.rating = 4.5
        mock_user.created_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = mappers.user_orm_to_response(mock_user)
        
        assert result.id == mock_user.id
        assert result.email == "test@example.com"
        assert result.name == "Test User"
        assert result.phone == "+1234567890"
        assert result.avatar_url == "http://example.com/avatar.jpg"
        assert result.rating == 4.5
    
    def test_user_orm_to_short_response(self):
        """Test mapping User ORM to UserShortResponse"""
        mock_user = MagicMock()
        mock_user.id = UUID("12345678-1234-5678-1234-567812345678")
        mock_user.name = "Test User"
        mock_user.avatar_url = "http://example.com/avatar.jpg"
        mock_user.rating = 4.5
        mock_user.phone = "+1234567890"
        
        result = mappers.user_orm_to_short_response(mock_user)
        
        assert result.id == mock_user.id
        assert result.name == "Test User"
        assert result.avatar_url == "http://example.com/avatar.jpg"
        assert result.rating == 4.5
        assert result.phone == "+1234567890"
    
    def test_user_create_to_internal(self):
        """Test mapping UserCreate to UserCreateInternal"""
        user_create = UserCreate(
            email="test@example.com",
            password="password123",
            name="Test User",
            phone="+1234567890"
        )
        
        result = mappers.user_create_to_internal(user_create, "hashed_password")
        
        assert result.email == "test@example.com"
        assert result.password_hash == "hashed_password"
        assert result.name == "Test User"
        assert result.phone == "+1234567890"
    
    def test_user_update_to_dict(self):
        """Test mapping UserUpdate to dict"""
        user_update = UserUpdate(
            name="New Name",
            phone="+0987654321"
        )
        
        result = mappers.user_update_to_dict(user_update)
        
        assert result == {"name": "New Name", "phone": "+0987654321"}
    
    def test_user_update_to_dict_with_none(self):
        """Test mapping UserUpdate with None values"""
        user_update = UserUpdate(name="New Name")
        
        result = mappers.user_update_to_dict(user_update)
        
        assert result == {"name": "New Name"}


class TestTripMappers:
    """Tests for Trip mappers"""
    
    def test_trip_orm_to_response(self):
        """Test mapping Trip ORM to TripResponse"""
        mock_trip = MagicMock()
        mock_trip.id = UUID("22345678-1234-5678-1234-567812345678")
        mock_trip.driver_id = UUID("12345678-1234-5678-1234-567812345678")
        mock_trip.from_city = "Moscow"
        mock_trip.to_city = "Saint Petersburg"
        mock_trip.departure_date = "2024-06-01"
        mock_trip.departure_time = "10:00"
        mock_trip.available_seats = 3
        mock_trip.price_per_seat = 1500
        mock_trip.description = "Comfortable trip"
        mock_trip.status = "active"
        mock_trip.created_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = mappers.trip_orm_to_response(mock_trip)
        
        assert result.id == mock_trip.id
        assert result.driver_id == mock_trip.driver_id
        assert result.from_city == "Moscow"
        assert result.to_city == "Saint Petersburg"
        assert result.available_seats == 3
        assert result.price_per_seat == 1500
        assert result.status == "active"
    
    def test_trip_orm_to_with_driver_response_with_driver(self):
        """Test mapping Trip ORM to TripWithDriverResponse with driver"""
        mock_trip = MagicMock()
        mock_trip.id = UUID("22345678-1234-5678-1234-567812345678")
        mock_trip.driver_id = UUID("12345678-1234-5678-1234-567812345678")
        mock_trip.from_city = "Moscow"
        mock_trip.to_city = "Saint Petersburg"
        mock_trip.departure_date = "2024-06-01"
        mock_trip.departure_time = "10:00"
        mock_trip.available_seats = 3
        mock_trip.price_per_seat = 1500
        mock_trip.status = "active"
        
        mock_driver = MagicMock()
        mock_driver.id = UUID("12345678-1234-5678-1234-567812345678")
        mock_driver.name = "Driver User"
        mock_driver.avatar_url = "http://example.com/driver.jpg"
        mock_driver.rating = 4.8
        
        result = mappers.trip_orm_to_with_driver_response(mock_trip, mock_driver)
        
        assert result.id == mock_trip.id
        assert result.driver is not None
        assert result.driver["name"] == "Driver User"
        assert result.driver["rating"] == 4.8
    
    def test_trip_orm_to_with_driver_response_without_driver(self):
        """Test mapping Trip ORM to TripWithDriverResponse without driver"""
        mock_trip = MagicMock()
        mock_trip.id = UUID("22345678-1234-5678-1234-567812345678")
        mock_trip.driver_id = UUID("12345678-1234-5678-1234-567812345678")
        mock_trip.from_city = "Moscow"
        mock_trip.to_city = "Saint Petersburg"
        mock_trip.departure_date = "2024-06-01"
        mock_trip.departure_time = "10:00"
        mock_trip.available_seats = 3
        mock_trip.price_per_seat = 1500
        mock_trip.status = "active"
        
        result = mappers.trip_orm_to_with_driver_response(mock_trip, None)
        
        assert result.id == mock_trip.id
        assert result.driver is None
    
    def test_trip_orm_to_driver_response(self):
        """Test mapping Trip ORM to TripDriverResponse"""
        mock_trip = MagicMock()
        mock_trip.id = UUID("22345678-1234-5678-1234-567812345678")
        mock_trip.from_city = "Moscow"
        mock_trip.to_city = "Saint Petersburg"
        mock_trip.departure_date = "2024-06-01"
        mock_trip.departure_time = "10:00"
        mock_trip.available_seats = 3
        mock_trip.price_per_seat = 1500
        mock_trip.status = "active"
        
        result = mappers.trip_orm_to_driver_response(mock_trip, 2)
        
        assert result.id == mock_trip.id
        assert result.passengers_count == 2
    
    def test_trip_create_to_internal(self):
        """Test mapping TripCreate to TripCreateInternal"""
        driver_id = UUID("12345678-1234-5678-1234-567812345678")
        trip_create = TripCreate(
            from_city="Moscow",
            to_city="Saint Petersburg",
            departure_date="2024-06-01",
            departure_time="10:00",
            available_seats=3,
            price_per_seat=1500,
            description="Comfortable trip"
        )
        
        result = mappers.trip_create_to_internal(trip_create, driver_id)
        
        assert result.driver_id == driver_id
        assert result.from_city == "Moscow"
        assert result.to_city == "Saint Petersburg"
        assert result.available_seats == 3
        assert result.price_per_seat == 1500
        assert result.status == "active"
    
    def test_trip_update_to_dict(self):
        """Test mapping TripUpdate to dict"""
        trip_update = TripUpdate(
            from_city="New City",
            available_seats=4
        )
        
        result = mappers.trip_update_to_dict(trip_update)
        
        assert result == {"from_city": "New City", "available_seats": 4}
    
    def test_trip_update_to_dict_with_none(self):
        """Test mapping TripUpdate with None values"""
        trip_update = TripUpdate(from_city="New City")
        
        result = mappers.trip_update_to_dict(trip_update)
        
        assert result == {"from_city": "New City"}


class TestRequestMappers:
    """Tests for Request mappers"""
    
    def test_request_orm_to_response(self):
        """Test mapping TripRequest ORM to TripRequestResponse"""
        mock_request = MagicMock()
        mock_request.id = UUID("32345678-1234-5678-1234-567812345678")
        mock_request.trip_id = UUID("22345678-1234-5678-1234-567812345678")
        mock_request.passenger_id = UUID("42345678-1234-5678-1234-567812345678")
        mock_request.seats_requested = 2
        mock_request.message = "Please take me"
        mock_request.status = "pending"
        mock_request.created_at = datetime(2024, 1, 1, 12, 0, 0)
        mock_request.updated_at = None
        
        mock_passenger = MagicMock()
        mock_passenger.id = UUID("42345678-1234-5678-1234-567812345678")
        mock_passenger.name = "Passenger User"
        mock_passenger.avatar_url = "http://example.com/passenger.jpg"
        mock_passenger.rating = 4.2
        mock_passenger.phone = "+1234567890"
        
        result = mappers.request_orm_to_response(mock_request, mock_passenger)
        
        assert result.id == mock_request.id
        assert result.passenger is not None
        assert result.passenger["name"] == "Passenger User"
        assert result.seats_requested == 2
        assert result.status == "pending"
    
    def test_request_create_to_internal(self):
        """Test mapping RequestCreate to RequestCreateInternal"""
        trip_id = UUID("22345678-1234-5678-1234-567812345678")
        passenger_id = UUID("42345678-1234-5678-1234-567812345678")
        request_create = RequestCreate(
            trip_id=trip_id,
            seats_requested=2,
            message="Please take me"
        )
        
        result = mappers.request_create_to_internal(request_create, passenger_id)
        
        assert result.trip_id == trip_id
        assert result.passenger_id == passenger_id
        assert result.seats_requested == 2
        assert result.message == "Please take me"
        assert result.status == "pending"
    
    def test_request_status_update_to_str(self):
        """Test mapping RequestStatusUpdate to string"""
        status_update = RequestStatusUpdate(status="confirmed")
        
        result = mappers.request_status_update_to_str(status_update)
        
        assert result == "confirmed"


class TestNotificationMappers:
    """Tests for Notification mappers"""
    
    def test_notification_orm_to_response(self):
        """Test mapping Notification ORM to NotificationResponse"""
        mock_notification = MagicMock()
        mock_notification.id = UUID("52345678-1234-5678-1234-567812345678")
        mock_notification.user_id = UUID("12345678-1234-5678-1234-567812345678")
        mock_notification.type = "request_confirmed"
        mock_notification.title = "Request Confirmed"
        mock_notification.message = "Your request has been confirmed"
        mock_notification.related_trip_id = None
        mock_notification.related_request_id = None
        mock_notification.is_read = False
        mock_notification.created_at = datetime(2024, 1, 1, 12, 0, 0)
        
        result = mappers.notification_orm_to_response(mock_notification)
        
        assert result.id == mock_notification.id
        assert result.type == "request_confirmed"
        assert result.title == "Request Confirmed"
        assert result.is_read is False
    
    def test_notification_create_to_dict(self):
        """Test mapping NotificationCreate to dict"""
        user_id = UUID("12345678-1234-5678-1234-567812345678")
        notification_create = NotificationCreate(
            user_id=user_id,
            type="request_received",
            title="New Request",
            message="You have a new request"
        )
        
        result = mappers.notification_create_to_dict(notification_create)
        
        assert result["user_id"] == user_id
        assert result["type"] == "request_received"
        assert result["title"] == "New Request"
        assert result["message"] == "You have a new request"