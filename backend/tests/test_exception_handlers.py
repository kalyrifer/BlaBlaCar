"""Tests for HTTP exception mapping.

This module tests that domain exceptions are correctly mapped to HTTP responses
with appropriate status codes.
"""
import pytest
from fastapi.testclient import TestClient
import pytest_asyncio

from app.main import app
from app.core.exceptions import (
    NotFoundError,
    ForbiddenError,
    NotEnoughSeatsError,
    InvalidStatusTransitionError,
    UserAlreadyExistsError,
    InvalidCredentialsError
)


class TestExceptionHandlers:
    """Test class for exception handlers."""

    @pytest.mark.asyncio
    async def test_not_found_error_returns_404(self):
        """Test that NotFoundError maps to HTTP 404."""
        from app.main import not_found_error_handler
        
        # Create a mock request
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        # Call the handler directly (it's async)
        exc = NotFoundError("Resource not found")
        response = await not_found_error_handler(MockRequest(), exc)
        
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_forbidden_error_returns_403(self):
        """Test that ForbiddenError maps to HTTP 403."""
        from app.main import forbidden_error_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        exc = ForbiddenError("Access forbidden")
        response = await forbidden_error_handler(MockRequest(), exc)
        
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_not_enough_seats_error_returns_409(self):
        """Test that NotEnoughSeatsError maps to HTTP 409."""
        from app.main import not_enough_seats_error_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        exc = NotEnoughSeatsError("Not enough available seats")
        response = await not_enough_seats_error_handler(MockRequest(), exc)
        
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_invalid_status_transition_error_returns_400(self):
        """Test that InvalidStatusTransitionError maps to HTTP 400."""
        from app.main import invalid_status_transition_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        exc = InvalidStatusTransitionError("Invalid status transition")
        response = await invalid_status_transition_handler(MockRequest(), exc)
        
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_user_already_exists_error_returns_400(self):
        """Test that UserAlreadyExistsError maps to HTTP 400."""
        from app.main import user_already_exists_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        exc = UserAlreadyExistsError("User already exists")
        response = await user_already_exists_handler(MockRequest(), exc)
        
        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_invalid_credentials_error_returns_401(self):
        """Test that InvalidCredentialsError maps to HTTP 401."""
        from app.main import invalid_credentials_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        exc = InvalidCredentialsError("Invalid credentials")
        response = await invalid_credentials_handler(MockRequest(), exc)
        
        assert response.status_code == 401


class TestExceptionMessages:
    """Test that exception messages are correctly passed to HTTP responses."""

    @pytest.mark.asyncio
    async def test_not_found_error_contains_message(self):
        """Test that NotFoundError response contains the error message."""
        from app.main import not_found_error_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        custom_message = "Custom not found message"
        exc = NotFoundError(custom_message)
        response = await not_found_error_handler(MockRequest(), exc)
        
        import json
        content = json.loads(response.body)
        assert content["detail"] == custom_message

    @pytest.mark.asyncio
    async def test_forbidden_error_contains_message(self):
        """Test that ForbiddenError response contains the error message."""
        from app.main import forbidden_error_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        custom_message = "Custom forbidden message"
        exc = ForbiddenError(custom_message)
        response = await forbidden_error_handler(MockRequest(), exc)
        
        import json
        content = json.loads(response.body)
        assert content["detail"] == custom_message

    @pytest.mark.asyncio
    async def test_not_enough_seats_error_contains_message(self):
        """Test that NotEnoughSeatsError response contains the error message."""
        from app.main import not_enough_seats_error_handler
        
        class MockRequest:
            def __init__(self):
                self.url = type('obj', (object,), {'path': '/test'})()
        
        custom_message = "Only 2 seats available"
        exc = NotEnoughSeatsError(custom_message)
        response = await not_enough_seats_error_handler(MockRequest(), exc)
        
        import json
        content = json.loads(response.body)
        assert content["detail"] == custom_message
