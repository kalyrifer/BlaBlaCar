"""
Prometheus metrics for monitoring application performance.

Provides metrics for:
- Request duration (histogram)
- Error rate (counter)
- Active users (gauge)
- Database connection status
"""
import logging
from time import time
from typing import Optional

from prometheus_client import Counter, Gauge, Histogram, Summary, CollectorRegistry, generate_latest

from app.core.config import settings

logger = logging.getLogger(__name__)

# Create a custom registry (can be used with /metrics endpoint)
registry = CollectorRegistry()

# Request metrics
HTTP_REQUESTS_TOTAL = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=registry
)

HTTP_REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint'],
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
    registry=registry
)

# Error metrics
ERRORS_TOTAL = Counter(
    'errors_total',
    'Total errors',
    ['type', 'endpoint'],
    registry=registry
)

# Active users
ACTIVE_USERS = Gauge(
    'active_users',
    'Number of currently active users',
    registry=registry
)

# Database metrics
DB_POOL_SIZE = Gauge(
    'db_pool_size',
    'Current database connection pool size',
    registry=registry
)

DB_POOL_ACTIVE = Gauge(
    'db_pool_active',
    'Number of active database connections',
    registry=registry
)

# Request count (for error rate calculation)
REQUESTS_TOTAL = Counter(
    'app_requests_total',
    'Total application requests',
    registry=registry
)

REQUESTS_ERRORS = Counter(
    'app_requests_errors_total',
    'Total application request errors',
    registry=registry
)


class MetricsMiddleware:
    """
    Middleware to collect Prometheus metrics for each request.
    """
    
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Skip metrics for prometheus endpoint
        path = scope.get("path", "")
        if path == "/metrics":
            await self.app(scope, receive, send)
            return
        
        method = scope.get("method", "GET")
        
        # Start timer
        start_time = time()
        
        # Custom send that captures status
        status_code = 200
        async def send_wrapper(message):
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = message.get("status", 200)
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Count error
            REQUESTS_ERRORS.inc()
            ERRORS_TOTAL.labels(type=type(e).__name__, endpoint=path).inc()
            raise
        finally:
            # Record duration
            duration = time() - start_time
            HTTP_REQUEST_DURATION.labels(
                method=method,
                endpoint=path
            ).observe(duration)
            
            # Count request
            HTTP_REQUESTS_TOTAL.labels(
                method=method,
                endpoint=path,
                status=status_code
            ).inc()
            REQUESTS_TOTAL.inc()
            
            # Track error rate
            if status_code >= 400:
                REQUESTS_ERRORS.inc()


def update_active_users(count: int) -> None:
    """Update the active users gauge."""
    ACTIVE_USERS.set(count)


def update_db_pool_metrics(size: int, active: int) -> None:
    """Update database pool metrics."""
    DB_POOL_SIZE.set(size)
    DB_POOL_ACTIVE.set(active)


def get_metrics() -> bytes:
    """Get Prometheus metrics in text format."""
    return generate_latest(registry)


# Decorator for manual timing
def track_duration(metric_name: str):
    """Decorator to track function execution time."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            start = time()
            try:
                return await func(*args, **kwargs)
            finally:
                duration = time() - start
                HTTP_REQUEST_DURATION.labels(
                    method="function",
                    endpoint=metric_name
                ).observe(duration)
        return wrapper
    return decorator


def increment_error(error_type: str, endpoint: str = "unknown") -> None:
    """Manually increment error counter."""
    ERRORS_TOTAL.labels(type=error_type, endpoint=endpoint).inc()
    REQUESTS_ERRORS.inc()