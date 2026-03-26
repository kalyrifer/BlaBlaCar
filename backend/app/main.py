"""
Точка входа FastAPI приложения.
Инициализирует приложение, подключает роутеры, настраивает CORS.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.api import auth, trips, requests, users, notifications, reviews
from app.core.config import settings
from app.core.database import (
    get_user_repo,
    get_trip_repo, 
    get_request_repo, 
    get_notification_repo,
    get_refresh_token_repo,
    init_postgres,
    create_tables
)
from app.core.exceptions import (
    NotFoundError,
    ForbiddenError,
    NotEnoughSeatsError,
    InvalidStatusTransitionError,
    UserAlreadyExistsError,
    InvalidCredentialsError
)
from app.core.middleware import RequestIDMiddleware
from app.core.rate_limiter import RateLimitMiddleware
from app.core.security_headers import SecurityHeadersMiddleware
from app.background.worker import (
    get_notification_queue,
    notification_worker,
    wait_for_queue_drain,
    set_notification_backend
)
from app.background.adapters import InProcessAdapter


# Global worker task reference
_worker_task: asyncio.Task = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Initializes the notification worker on startup and gracefully shuts it down.
    """
    global _worker_task
    
    # Startup: Initialize PostgreSQL if enabled
    if settings.USE_POSTGRESQL:
        init_postgres()
        await create_tables()
        print("[OK] PostgreSQL initialized")
    
    # Startup: Initialize notification backend and start worker
    notification_repo = get_notification_repo()
    backend = InProcessAdapter(notification_repo)
    await backend.initialize()
    set_notification_backend(backend)
    
    # Start the notification worker
    queue = get_notification_queue()
    _worker_task = asyncio.create_task(notification_worker(queue))
    
    yield  # App is running
    
    # Shutdown: Gracefully stop the worker
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    
    # Wait for queue to drain
    queue = get_notification_queue()
    await wait_for_queue_drain(queue, timeout=5.0)
    
    # Shutdown backend
    await backend.shutdown()


app = FastAPI(
    title="Ride Sharing API",
    version="1.0.0",
    description="MVP API для поиска попутчиков",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security headers (CSP, X-Frame-Options, etc.)
app.add_middleware(SecurityHeadersMiddleware)

# Rate limiting
if settings.RATE_LIMIT_ENABLED:
    app.add_middleware(RateLimitMiddleware)

# Request ID middleware for logging
app.add_middleware(RequestIDMiddleware)


# Exception handlers for domain exceptions
@app.exception_handler(NotFoundError)
async def not_found_error_handler(request: Request, exc: NotFoundError):
    """Handle NotFoundError exceptions -> HTTP 404"""
    return JSONResponse(
        status_code=404,
        content={"detail": exc.message}
    )


@app.exception_handler(ForbiddenError)
async def forbidden_error_handler(request: Request, exc: ForbiddenError):
    """Handle ForbiddenError exceptions -> HTTP 403"""
    return JSONResponse(
        status_code=403,
        content={"detail": exc.message}
    )


@app.exception_handler(NotEnoughSeatsError)
async def not_enough_seats_error_handler(request: Request, exc: NotEnoughSeatsError):
    """Handle NotEnoughSeatsError exceptions -> HTTP 409"""
    return JSONResponse(
        status_code=409,
        content={"detail": exc.message}
    )


@app.exception_handler(InvalidStatusTransitionError)
async def invalid_status_transition_handler(request: Request, exc: InvalidStatusTransitionError):
    """Handle InvalidStatusTransitionError exceptions -> HTTP 400"""
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )


@app.exception_handler(UserAlreadyExistsError)
async def user_already_exists_handler(request: Request, exc: UserAlreadyExistsError):
    """Handle UserAlreadyExistsError exceptions -> HTTP 400"""
    return JSONResponse(
        status_code=400,
        content={"detail": exc.message}
    )


@app.exception_handler(InvalidCredentialsError)
async def invalid_credentials_handler(request: Request, exc: InvalidCredentialsError):
    """Handle InvalidCredentialsError exceptions -> HTTP 401"""
    return JSONResponse(
        status_code=401,
        content={"detail": exc.message}
    )


# Роутеры
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(trips.router, prefix="/api/trips", tags=["trips"])
app.include_router(requests.router, prefix="/api/requests", tags=["requests"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["reviews"])


@app.get("/")
async def root():
    return {"message": "Ride Sharing API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint with database status"""
    from app.core.database import engine
    from app.core.config import settings
    
    status = {"status": "ok", "database": "in-memory"}
    
    if settings.USE_POSTGRESQL and engine is not None:
        try:
            # Test database connection
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            status["database"] = "postgresql"
            status["postgres_status"] = "connected"
        except Exception as e:
            status["status"] = "error"
            status["postgres_status"] = f"error: {str(e)}"
    
    return status


@app.get("/health/live")
async def liveness_check():
    """
    Liveness probe endpoint.
    
    Returns 200 if the application is running.
    Used by Kubernetes to know when to restart the container.
    """
    return {"status": "alive"}


@app.get("/health/ready")
async def readiness_check():
    """
    Readiness probe endpoint.
    
    Returns 200 if the application is ready to accept traffic.
    Includes database connectivity check.
    """
    from app.core.database import engine
    from app.core.config import settings
    from sqlalchemy import text
    
    checks = {
        "status": "ready",
        "checks": {}
    }
    
    # Check database connectivity
    if settings.USE_POSTGRESQL and engine is not None:
        try:
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            checks["checks"]["database"] = "ok"
        except Exception as e:
            checks["status"] = "not_ready"
            checks["checks"]["database"] = f"error: {str(e)}"
    else:
        checks["checks"]["database"] = "in-memory (no check needed)"
    
    # Return appropriate status code
    if checks["status"] != "ready":
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=503,
            content=checks
        )
    
    return checks


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from app.core.metrics import get_metrics
    from fastapi.responses import Response
    
    return Response(
        content=get_metrics(),
        media_type="text/plain"
    )


@app.get("/docs")
async def docs_redirect():
    """Redirect to OpenAPI docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/redoc")
