"""
Точка входа FastAPI приложения.
Инициализирует приложение, подключает роутеры, настраивает CORS.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, trips, requests, users, notifications
from app.core.config import settings
from app.core.database import (
    get_user_repo,
    get_trip_repo, 
    get_request_repo, 
    get_notification_repo,
    get_refresh_token_repo
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


@app.get("/")
async def root():
    return {"message": "Ride Sharing API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.get("/docs")
async def docs_redirect():
    """Redirect to OpenAPI docs"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/redoc")
