"""
Инициализация базы данных с поддержкой PostgreSQL и in-memory storage.
"""
from app.core.config import settings
from typing import Optional

# Import in-memory repositories
from app.repositories.inmemory.user_repo import InMemoryUserRepository
from app.repositories.inmemory.trip_repo import InMemoryTripRepository
from app.repositories.inmemory.request_repo import InMemoryRequestRepository
from app.repositories.inmemory.notification_repo import InMemoryNotificationRepository
from app.repositories.inmemory.refresh_token_repo import InMemoryRefreshTokenRepository
from app.repositories.interfaces import IUserRepository, ITripRepository, IRequestRepository, INotificationRepository, IRefreshTokenRepository

# SQLAlchemy imports for PostgreSQL - import Base from models
from app.db.models.base import Base
from app.db.models import user, trip, trip_request, notification, refresh_token  # Import all models
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Async engine и session factory для PostgreSQL
engine = None
async_session_maker = None


class Database:
    """Database container - поддерживает как in-memory, так и PostgreSQL"""
    
    def __init__(self, use_pg: bool = False):
        self.use_pg = use_pg
        
        if use_pg and settings.USE_POSTGRESQL:
            # PostgreSQL mode - используем SQLAlchemy
            self._pg_session: Optional[AsyncSession] = None
        else:
            # In-memory mode - используем репозитории
            self.users = InMemoryUserRepository()
            self.trips = InMemoryTripRepository()
            self.requests = InMemoryRequestRepository()
            self.notifications = InMemoryNotificationRepository()
            self.refresh_tokens = InMemoryRefreshTokenRepository()
    
    @property
    def pg_session(self) -> Optional[AsyncSession]:
        """Get PostgreSQL session"""
        return getattr(self, '_pg_session', None)
    
    def set_session(self, session: AsyncSession):
        """Set PostgreSQL session"""
        self._pg_session = session


# Singleton instance - определяется при инициализации
db: Database = Database(use_pg=settings.USE_POSTGRESQL)


def init_postgres():
    """Инициализация PostgreSQL движка"""
    global engine, async_session_maker, db
    
    if settings.USE_POSTGRESQL:
        # Создаем async engine для PostgreSQL
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20
        )
        
        # Создаем session maker
        async_session_maker = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Обновляем db для использования PostgreSQL
        db = Database(use_pg=True)
        
        return engine, async_session_maker
    return None, None


def get_db() -> Database:
    """Get database instance"""
    return db


def get_user_repo() -> IUserRepository:
    """Get user repository"""
    if settings.USE_POSTGRESQL:
        from app.db.repositories.pg_user_repo import PGUserRepository
        return PGUserRepository(db.pg_session)
    return db.users


def get_trip_repo() -> ITripRepository:
    """Get trip repository"""
    if settings.USE_POSTGRESQL:
        from app.db.repositories.pg_trip_repo import PGTripRepository
        return PGTripRepository(db.pg_session)
    return db.trips


def get_request_repo() -> IRequestRepository:
    """Get request repository"""
    if settings.USE_POSTGRESQL:
        from app.db.repositories.pg_request_repo import PGRequestRepository
        return PGRequestRepository(db.pg_session)
    return db.requests


def get_notification_repo() -> INotificationRepository:
    """Get notification repository"""
    if settings.USE_POSTGRESQL:
        from app.db.repositories.pg_notification_repo import PGNotificationRepository
        return PGNotificationRepository(db.pg_session)
    return db.notifications


def get_refresh_token_repo() -> IRefreshTokenRepository:
    """Get refresh token repository"""
    if settings.USE_POSTGRESQL:
        from app.db.repositories.pg_refresh_token_repo import PGRefreshTokenRepository
        return PGRefreshTokenRepository(db.pg_session)
    return db.refresh_tokens


async def get_db_session() -> AsyncSession:
    """Получить async сессию PostgreSQL"""
    if not settings.USE_POSTGRESQL or async_session_maker is None:
        raise RuntimeError("PostgreSQL is not enabled")
    
    async with async_session_maker() as session:
        yield session


async def create_tables():
    """Создать все таблицы в PostgreSQL"""
    if settings.USE_POSTGRESQL and engine is not None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
