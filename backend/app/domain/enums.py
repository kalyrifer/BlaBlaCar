"""Domain enums for status and types"""
from enum import Enum


class TripStatus(str, Enum):
    """Trip status enum"""
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FULL = "full"


class RequestStatus(str, Enum):
    """Request status enum"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class NotificationType(str, Enum):
    """Notification type enum"""
    REQUEST_RECEIVED = "request_received"
    REQUEST_CONFIRMED = "request_confirmed"
    REQUEST_REJECTED = "request_rejected"
    TRIP_CANCELLED = "trip_cancelled"


# Status transition rules

# Request status transitions: what statuses can transition to what
REQUEST_STATUS_TRANSITIONS = {
    RequestStatus.PENDING: [RequestStatus.CONFIRMED, RequestStatus.REJECTED, RequestStatus.CANCELLED],
    RequestStatus.CONFIRMED: [RequestStatus.CANCELLED],
    RequestStatus.REJECTED: [RequestStatus.PENDING],  # Can resubmit
    RequestStatus.CANCELLED: [RequestStatus.PENDING],  # Can resubmit
}

# Trip status transitions: what statuses can transition to what
TRIP_STATUS_TRANSITIONS = {
    TripStatus.ACTIVE: [TripStatus.COMPLETED, TripStatus.CANCELLED, TripStatus.FULL],
    TripStatus.COMPLETED: [],  # Terminal state
    TripStatus.CANCELLED: [],  # Terminal state
    TripStatus.FULL: [TripStatus.COMPLETED, TripStatus.CANCELLED],  # Can still complete or cancel
}


def is_valid_request_status_transition(old: RequestStatus, new: RequestStatus) -> bool:
    """Check if request status transition is valid"""
    allowed = REQUEST_STATUS_TRANSITIONS.get(old, [])
    return new in allowed


def is_valid_trip_status_transition(old: TripStatus, new: TripStatus) -> bool:
    """Check if trip status transition is valid"""
    allowed = TRIP_STATUS_TRANSITIONS.get(old, [])
    return new in allowed


class InvalidStatusTransitionError(Exception):
    """Raised when an invalid status transition is attempted"""
    pass
