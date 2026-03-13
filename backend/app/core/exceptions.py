"""Centralized domain exceptions for the application.

This module contains all domain-specific exceptions that are used throughout
the application services. These exceptions are mapped to HTTP responses
in the main application.
"""


class NotFoundError(Exception):
    """Base exception for resource not found errors.
    
    This is typically mapped to HTTP 404 response.
    """
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(self.message)


class ForbiddenError(Exception):
    """Exception for access forbidden errors.
    
    This is mapped to HTTP 403 Forbidden response.
    """
    def __init__(self, message: str = "Access forbidden"):
        self.message = message
        super().__init__(self.message)


class UserAlreadyExistsError(Exception):
    """Exception raised when attempting to create a user that already exists.
    
    This is typically mapped to HTTP 400 or 409 response.
    """
    def __init__(self, message: str = "User already exists"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsError(Exception):
    """Exception raised when credentials are invalid.
    
    This is mapped to HTTP 401 Unauthorized response.
    """
    def __init__(self, message: str = "Invalid credentials"):
        self.message = message
        super().__init__(self.message)


class NotEnoughSeatsError(Exception):
    """Exception raised when there are not enough available seats.
    
    This is mapped to HTTP 409 Conflict response.
    """
    def __init__(self, message: str = "Not enough available seats"):
        self.message = message
        super().__init__(self.message)


class InvalidStatusTransitionError(Exception):
    """Exception raised when an invalid status transition is attempted.
    
    This is typically mapped to HTTP 400 Bad Request response.
    """
    def __init__(self, message: str = "Invalid status transition"):
        self.message = message
        super().__init__(self.message)
