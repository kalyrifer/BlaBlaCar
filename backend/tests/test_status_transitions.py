"""Tests for status transition validation"""
import pytest
from app.domain.enums import (
    RequestStatus,
    TripStatus,
    is_valid_request_status_transition,
    is_valid_trip_status_transition,
    InvalidStatusTransitionError,
)


class TestRequestStatusTransitions:
    """Tests for request status transitions"""
    
    def test_pending_to_confirmed_valid(self):
        """pending -> confirmed is valid"""
        assert is_valid_request_status_transition(
            RequestStatus.PENDING, 
            RequestStatus.CONFIRMED
        ) is True
    
    def test_pending_to_rejected_valid(self):
        """pending -> rejected is valid"""
        assert is_valid_request_status_transition(
            RequestStatus.PENDING, 
            RequestStatus.REJECTED
        ) is True
    
    def test_pending_to_cancelled_valid(self):
        """pending -> cancelled is valid"""
        assert is_valid_request_status_transition(
            RequestStatus.PENDING, 
            RequestStatus.CANCELLED
        ) is True
    
    def test_confirmed_to_cancelled_valid(self):
        """confirmed -> cancelled is valid"""
        assert is_valid_request_status_transition(
            RequestStatus.CONFIRMED, 
            RequestStatus.CANCELLED
        ) is True
    
    def test_confirmed_to_rejected_invalid(self):
        """confirmed -> rejected is invalid"""
        assert is_valid_request_status_transition(
            RequestStatus.CONFIRMED, 
            RequestStatus.REJECTED
        ) is False
    
    def test_confirmed_to_pending_invalid(self):
        """confirmed -> pending is invalid"""
        assert is_valid_request_status_transition(
            RequestStatus.CONFIRMED, 
            RequestStatus.PENDING
        ) is False
    
    def test_rejected_to_pending_valid(self):
        """rejected -> pending is valid (can resubmit)"""
        assert is_valid_request_status_transition(
            RequestStatus.REJECTED, 
            RequestStatus.PENDING
        ) is True
    
    def test_cancelled_to_pending_valid(self):
        """cancelled -> pending is valid (can resubmit)"""
        assert is_valid_request_status_transition(
            RequestStatus.CANCELLED, 
            RequestStatus.PENDING
        ) is True
    
    def test_rejected_to_confirmed_invalid(self):
        """rejected -> confirmed is invalid"""
        assert is_valid_request_status_transition(
            RequestStatus.REJECTED, 
            RequestStatus.CONFIRMED
        ) is False


class TestTripStatusTransitions:
    """Tests for trip status transitions"""
    
    def test_active_to_completed_valid(self):
        """active -> completed is valid"""
        assert is_valid_trip_status_transition(
            TripStatus.ACTIVE, 
            TripStatus.COMPLETED
        ) is True
    
    def test_active_to_cancelled_valid(self):
        """active -> cancelled is valid"""
        assert is_valid_trip_status_transition(
            TripStatus.ACTIVE, 
            TripStatus.CANCELLED
        ) is True
    
    def test_active_to_full_valid(self):
        """active -> full is valid"""
        assert is_valid_trip_status_transition(
            TripStatus.ACTIVE, 
            TripStatus.FULL
        ) is True
    
    def test_full_to_completed_valid(self):
        """full -> completed is valid"""
        assert is_valid_trip_status_transition(
            TripStatus.FULL, 
            TripStatus.COMPLETED
        ) is True
    
    def test_full_to_cancelled_valid(self):
        """full -> cancelled is valid"""
        assert is_valid_trip_status_transition(
            TripStatus.FULL, 
            TripStatus.CANCELLED
        ) is True
    
    def test_completed_to_anything_invalid(self):
        """completed -> anything is invalid (terminal state)"""
        assert is_valid_trip_status_transition(
            TripStatus.COMPLETED, 
            TripStatus.ACTIVE
        ) is False
        assert is_valid_trip_status_transition(
            TripStatus.COMPLETED, 
            TripStatus.CANCELLED
        ) is False
        assert is_valid_trip_status_transition(
            TripStatus.COMPLETED, 
            TripStatus.FULL
        ) is False
    
    def test_cancelled_to_anything_invalid(self):
        """cancelled -> anything is invalid (terminal state)"""
        assert is_valid_trip_status_transition(
            TripStatus.CANCELLED, 
            TripStatus.ACTIVE
        ) is False
        assert is_valid_trip_status_transition(
            TripStatus.CANCELLED, 
            TripStatus.COMPLETED
        ) is False
        assert is_valid_trip_status_transition(
            TripStatus.CANCELLED, 
            TripStatus.FULL
        ) is False
