"""Request ID middleware for tracking requests.

This middleware adds X-Request-ID header to responses and logs request details.
"""
import time
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.logger import get_logger, set_request_id, clear_request_id

logger = get_logger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware that adds X-Request-ID to requests and logs request metrics."""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process the request and add request ID.
        
        Args:
            request: The incoming request
            call_next: The next middleware/handler in the chain
            
        Returns:
            Response with X-Request-ID header
        """
        # Get request_id from header or generate new one
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid4())
        
        # Set request_id in context for logging
        set_request_id(request_id)
        
        # Record start time
        start_time = time.perf_counter()
        
        # Log request start
        client_host = request.client.host if request.client else "unknown"
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "client_host": client_host,
            }
        )
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Calculate latency
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Log request end
            logger.info(
                "Request completed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                    "latency_ms": round(latency_ms, 2),
                }
            )
            
            # Add X-Request-ID header to response
            response.headers["X-Request-ID"] = request_id
            
            return response
            
        except Exception as e:
            # Calculate latency for error case
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Log error
            logger.error(
                "Request failed",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": 500,
                    "latency_ms": round(latency_ms, 2),
                    "error": str(e),
                }
            )
            raise
            
        finally:
            # Clear request_id from context
            clear_request_id()
