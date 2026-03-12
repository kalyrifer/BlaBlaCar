"""
Точка входа FastAPI приложения.
Инициализирует приложение, подключает роутеры, настраивает CORS.
"""
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
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
