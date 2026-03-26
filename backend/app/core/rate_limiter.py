"""
Rate limiting middleware for API protection.
Implements token bucket algorithm for API rate limiting,
login attempt tracking, and IP blocking.
"""
import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from uuid import UUID

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Rate limiter using token bucket algorithm.
    
    Tracks requests per IP address and provides:
    - API rate limiting (100 requests/minute)
    - Login attempt limiting (5 attempts/15 minutes)
    - IP blocking (24 hours)
    """
    
    def __init__(
        self,
        requests_per_minute: int = 100,
        login_attempts: int = 5,
        login_window_minutes: int = 15,
        block_duration_hours: int = 24
    ):
        self.requests_per_minute = requests_per_minute
        self.login_attempts = login_attempts
        self.login_window = timedelta(minutes=login_window_minutes)
        self.block_duration = timedelta(hours=block_duration_hours)
        
        # Token bucket state: {ip: (tokens, last_refill_time)}
        self._api_buckets: Dict[str, Tuple[int, float]] = defaultdict(lambda: (requests_per_minute, time.time()))
        
        # Login attempts: {ip: [(attempt_time, success)]}
        self._login_attempts: Dict[str, list] = defaultdict(list)
        
        # Blocked IPs: {ip: unblock_time}
        self._blocked_ips: Dict[str, datetime] = {}
        
        # Lock for thread safety
        import threading
        self._lock = threading.Lock()
    
    def _refill_bucket(self, ip: str) -> int:
        """Refill token bucket based on elapsed time."""
        current_time = time.time()
        tokens, last_refill = self._api_buckets[ip]
        
        # Calculate time passed and add tokens (1 per second)
        seconds_passed = current_time - last_refill
        new_tokens = min(
            self.requests_per_minute,
            tokens + int(seconds_passed)
        )
        
        self._api_buckets[ip] = (new_tokens, current_time)
        return new_tokens
    
    def check_api_rate_limit(self, ip: str) -> Tuple[bool, int]:
        """
        Check if request is within rate limit.
        
        Returns:
            Tuple of (allowed, remaining_tokens)
        """
        # Check if IP is blocked
        if self.is_ip_blocked(ip):
            return False, 0
        
        with self._lock:
            tokens = self._refill_bucket(ip)
            
            if tokens > 0:
                # Consume one token
                self._api_buckets[ip] = (tokens - 1, time.time())
                return True, tokens - 1
            
            return False, 0
    
    def record_login_attempt(self, ip: str, success: bool) -> bool:
        """
        Record a login attempt.
        
        Returns:
            True if login is allowed, False if too many attempts
        """
        # Check if IP is blocked
        if self.is_ip_blocked(ip):
            return False
        
        current_time = datetime.utcnow()
        
        with self._lock:
            # Clean old attempts outside the window
            cutoff = current_time - self.login_window
            self._login_attempts[ip] = [
                attempt for attempt in self._login_attempts[ip]
                if attempt[0] > cutoff
            ]
            
            # If not a success, count this attempt
            if not success:
                self._login_attempts[ip].append((current_time, success))
                
                # Check if exceeded limit
                if len(self._login_attempts[ip]) >= self.login_attempts:
                    self._block_ip(ip)
                    logger.warning(f"IP {ip} blocked due to failed login attempts")
                    return False
            
            return True
    
    def _block_ip(self, ip: str) -> None:
        """Block an IP address."""
        self._blocked_ips[ip] = datetime.utcnow() + self.block_duration
    
    def is_ip_blocked(self, ip: str) -> bool:
        """Check if IP is currently blocked."""
        with self._lock:
            if ip in self._blocked_ips:
                unblock_time = self._blocked_ips[ip]
                if datetime.utcnow() > unblock_time:
                    # Block expired, clean up
                    del self._blocked_ips[ip]
                    if ip in self._api_buckets:
                        del self._api_buckets[ip]
                    if ip in self._login_attempts:
                        del self._login_attempts[ip]
                    return False
                return True
            return False
    
    def get_block_time_remaining(self, ip: str) -> Optional[int]:
        """Get remaining block time in seconds."""
        with self._lock:
            if ip in self._blocked_ips:
                remaining = self._blocked_ips[ip] - datetime.utcnow()
                return max(0, int(remaining.total_seconds()))
        return None


# Global rate limiter instance
rate_limiter = RateLimiter(
    requests_per_minute=settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
    login_attempts=settings.RATE_LIMIT_LOGIN_ATTEMPTS,
    login_window_minutes=settings.RATE_LIMIT_LOGIN_WINDOW_MINUTES,
    block_duration_hours=settings.RATE_LIMIT_IP_BLOCK_HOURS
)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    FastAPI middleware for rate limiting.
    
    Applies rate limiting to all API endpoints.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        if settings.RATE_LIMIT_ENABLED:
            allowed, remaining = rate_limiter.check_api_rate_limit(client_ip)
            
            if not allowed:
                block_time = rate_limiter.get_block_time_remaining(client_ip)
                logger.warning(
                    f"Rate limit exceeded for IP {client_ip}, "
                    f"path: {request.url.path}"
                )
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Too many requests",
                        "message": "Rate limit exceeded. Please try again later.",
                        "retry_after": block_time or 60
                    }
                )
            
            # Add rate limit headers
            response = await call_next(request)
            response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS_PER_MINUTE)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            return response
        
        return await call_next(request)


def check_login_rate_limit(ip: str) -> bool:
    """
    Check if login is allowed for the given IP.
    
    Returns:
        True if login is allowed, False if rate limited
    """
    return rate_limiter.record_login_attempt(ip, success=False)


def record_login_success(ip: str) -> None:
    """Record successful login to reset failed attempt counter."""
    rate_limiter.record_login_attempt(ip, success=True)


def is_ip_blocked(ip: str) -> bool:
    """Check if IP is blocked."""
    return rate_limiter.is_ip_blocked(ip)


def get_block_time_remaining(ip: str) -> Optional[int]:
    """Get remaining block time in seconds."""
    return rate_limiter.get_block_time_remaining(ip)