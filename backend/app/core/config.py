"""
Конфигурация приложения через переменные окружения.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }
    
    # App
    APP_NAME: str = "RoadMate API"
    DEBUG: bool = True
    
    # JWT - RS256 with RSA keys
    JWT_ALGORITHM: str = "RS256"
    JWT_PUBLIC_KEY_PATH: str = "./keys/public.pem"
    JWT_PRIVATE_KEY_PATH: str = "./keys/private.pem"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15  # Short-lived access tokens
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7  # Longer-lived refresh tokens
    
    # JWT Secret (fallback for development, will use RSA in production)
    JWT_SECRET_KEY: str = "dev-secret-key-change-in-production"
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]
    
    # Database
    USE_POSTGRESQL: bool = False
    DATABASE_URL: str = "sqlite:///./app.db"
    
    # Database connection pool settings
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 15
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 1800
    
    # Database backup settings
    BACKUP_ENABLED: bool = True
    BACKUP_DIR: str = "./backups"
    BACKUP_RETENTION_DAYS: int = 7
    
    # Rate limiting settings
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 100
    RATE_LIMIT_LOGIN_ATTEMPTS: int = 5
    RATE_LIMIT_LOGIN_WINDOW_MINUTES: int = 15
    RATE_LIMIT_IP_BLOCK_HOURS: int = 24
    
    # Security settings
    CSRF_ENABLED: bool = True
    CSP_ENABLED: bool = True
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_JSON_FORMAT: bool = True
    
    # Monitoring settings
    PROMETHEUS_ENABLED: bool = True
    METRICS_PORT: int = 9090
    
    # Alert thresholds
    ERROR_RATE_THRESHOLD: float = 5.0  # percent


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
