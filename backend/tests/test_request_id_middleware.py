"""Tests for Request ID middleware and structured logging.

This module tests that X-Request-ID header is properly added to responses
and that logs contain the request_id.
"""
import pytest
from fastapi.testclient import TestClient
import json

from app.main import app


class TestRequestIDMiddleware:
    """Test class for RequestIDMiddleware."""

    def test_request_id_header_added_to_response(self):
        """Test that X-Request-ID header is added to response."""
        with TestClient(app) as client:
            response = client.get("/health")
            
            assert response.status_code == 200
            assert "X-Request-ID" in response.headers
            assert response.headers["X-Request-ID"] != ""

    def test_request_id_header_preserved_if_provided(self):
        """Test that X-Request-ID header is preserved if provided."""
        custom_request_id = "custom-request-id-12345"
        
        with TestClient(app) as client:
            response = client.get(
                "/health",
                headers={"X-Request-ID": custom_request_id}
            )
            
            assert response.status_code == 200
            assert response.headers["X-Request-ID"] == custom_request_id

    def test_request_id_is_valid_uuid(self):
        """Test that generated X-Request-ID is a valid UUID."""
        import uuid
        
        with TestClient(app) as client:
            response = client.get("/health")
            
            request_id = response.headers["X-Request-ID"]
            
            # Should be a valid UUID
            try:
                uuid.UUID(request_id)
            except ValueError:
                pytest.fail(f"X-Request-ID '{request_id}' is not a valid UUID")

    def test_all_endpoints_have_request_id(self):
        """Test that all endpoints return X-Request-ID header."""
        with TestClient(app) as client:
            # Test multiple endpoints
            endpoints = [
                "/health",
                "/",
                "/docs",
            ]
            
            for endpoint in endpoints:
                response = client.get(endpoint)
                assert "X-Request-ID" in response.headers, f"Missing X-Request-ID for {endpoint}"


class TestStructuredLogging:
    """Test class for structured logging."""

    def test_logger_outputs_json(self, capsys):
        """Test that logger outputs valid JSON."""
        from app.core.logger import get_logger
        
        logger = get_logger("test")
        logger.info("Test message")
        
        captured = capsys.readouterr()
        
        # Should be valid JSON
        try:
            log_data = json.loads(captured.out.strip())
            assert log_data["message"] == "Test message"
            assert "timestamp" in log_data
            assert "level" in log_data
        except json.JSONDecodeError:
            pytest.fail(f"Logger output is not valid JSON: {captured.out}")

    def test_logger_includes_request_id_in_context(self, capsys):
        """Test that logger includes request_id when set in context."""
        from app.core.logger import get_logger, set_request_id, clear_request_id
        
        test_request_id = "test-request-id-123"
        set_request_id(test_request_id)
        
        try:
            logger = get_logger("test")
            logger.info("Test message with request_id")
            
            captured = capsys.readouterr()
            log_data = json.loads(captured.out.strip())
            
            assert log_data["request_id"] == test_request_id
        finally:
            clear_request_id()

    def test_logger_includes_extra_fields(self, capsys):
        """Test that logger includes extra fields in output."""
        from app.core.logger import get_logger
        
        logger = get_logger("test")
        logger.info(
            "Test message",
            extra={"custom_field": "custom_value", "user_id": "user-123"}
        )
        
        captured = capsys.readouterr()
        log_data = json.loads(captured.out.strip())
        
        assert log_data["custom_field"] == "custom_value"
        assert log_data["user_id"] == "user-123"


class TestRequestLogging:
    """Test that requests are properly logged."""

    def test_request_start_is_logged(self, capsys):
        """Test that request start is logged."""
        with TestClient(app) as client:
            client.get("/health")
        
        captured = capsys.readouterr()
        
        # Check that request logs exist
        lines = captured.out.strip().split('\n')
        
        # Find log lines for this request
        request_logs = [json.loads(line) for line in lines if line.strip()]
        
        # Should have at least 2 logs: request start and request completed
        assert len(request_logs) >= 2
        
        # Check for request started log
        start_logs = [log for log in request_logs if "Request started" in log.get("message", "")]
        assert len(start_logs) > 0

    def test_request_logs_contain_method_and_path(self, capsys):
        """Test that request logs contain method and path."""
        with TestClient(app) as client:
            client.get("/health")
        
        captured = capsys.readouterr()
        
        lines = captured.out.strip().split('\n')
        log_data = json.loads(lines[0])
        
        assert "method" in log_data
        assert "path" in log_data
