"""
Точка входа FastAPI приложения.
Инициализирует приложение, подключает роутеры, настраивает CORS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import auth, trips, requests, users, notifications
from app.core.config import settings

app = FastAPI(
    title="Ride Sharing API",
    version="1.0.0",
    description="MVP API для поиска попутчиков"
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
