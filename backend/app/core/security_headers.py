"""
Security middleware for CSRF protection and CSP headers.
Provides protection against Cross-Site Request Forgery and
Content Security Policy enforcement.
"""
import logging
import secrets
from typing import Optional
from datetime import datetime, timedelta

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.datastructures import Headers

from app.core.config import settings

logger = logging.getLogger(__name__)


class CSRFTokenManager:
    """
    CSRF token manager for state-changing operations.
    
    Generates and validates CSRF tokens for POST, PUT, DELETE requests.
    """
    
    def __init__(self, token_length: int = 32):
        self.token_length = token_length
    
    def generate_token(self) -> str:
        """Generate a new CSRF token."""
        return secrets.token_urlsafe(self.token_length)
    
    def validate_token(self, token: str, expected: str) -> bool:
        """Validate a CSRF token using constant-time comparison."""
        if not token or not expected:
            return False
        # Use constant-time comparison to prevent timing attacks
        return secrets.compare_digest(token, expected)


# Global CSRF manager
csrf_manager = CSRFTokenManager()


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers including CSP.
    
    Adds:
    - Content-Security-Policy
    - X-Content-Type-Options
    - X-Frame-Options
    - X-XSS-Protection
    - Referrer-Policy
    """
    
    # CSP policy - restricts sources for content
    CSP_POLICY = (
        "default-src 'self'; "
        "script-src 'self'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' data: https:; "
        "font-src 'self'; "
        "connect-src 'self'; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        if settings.CSP_ENABLED:
            # Content Security Policy
            response.headers["Content-Security-Policy"] = self.CSP_POLICY
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer-Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions-Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=()"
        )
        
        return response


def generate_csrf_token() -> str:
    """Generate a new CSRF token."""
    return csrf_manager.generate_token()


def validate_csrf_token(token: str, expected: str) -> bool:
    """Validate a CSRF token."""
    return csrf_manager.validate_token(token, expected)


def get_request_csrf_token(request: Request) -> Optional[str]:
    """
    Extract CSRF token from request.
    
    Looks in:
    1. X-CSRF-Token header
    2. X-XSRF-Token header
    3. csrf token in body (for form submissions)
    """
    # Check headers first
    headers: Headers = request.headers
    token = headers.get("x-csrf-token") or headers.get("x-xsrf-token")
    
    if token:
        return token
    
    # Check body for form data (only for POST requests)
    if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
        try:
            # For form data
            content_type = headers.get("content-type", "")
            if "application/x-www-form-urlencoded" in content_type:
                # Would need to parse body - not recommended for async
                pass
            elif "multipart/form-data" in content_type:
                # Would need to parse multipart
                pass
        except Exception:
            pass
    
    return None


def is_safe_method(method: str) -> bool:
    """Check if HTTP method is read-only (safe)."""
    return method in ["GET", "HEAD", "OPTIONS", "TRACE"]


def requires_csrf_protection(method: str) -> bool:
    """Check if method requires CSRF protection."""
    return method in ["POST", "PUT", "PATCH", "DELETE"]