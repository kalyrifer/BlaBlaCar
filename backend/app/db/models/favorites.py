"""SQLAlchemy FavoriteTrip ORM model"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.models.base import Base


class FavoriteTrip(Base):
    """SQLAlchemy FavoriteTrip model - saved trips by users"""
    __tablename__ = "favorite_trips"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True
    )
    trip_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("trips.id"), 
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )


class RouteSubscription(Base):
    """SQLAlchemy RouteSubscription model - notifications for routes"""
    __tablename__ = "route_subscriptions"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True
    )
    from_city: Mapped[str] = mapped_column(String(255), nullable=False)
    to_city: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Optional geolocation for more precise matching
    from_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    from_lon: Mapped[Optional[float]] = mapped_column(nullable=True)
    to_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    to_lon: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # Notification preferences
    notify_on_new_trips: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notify_on_price_drop: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    min_seats: Mapped[int] = mapped_column(nullable=False, default=1)
    max_price_per_seat: Mapped[Optional[int]] = mapped_column(nullable=True)
    
    # Active status
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), 
        nullable=True, 
        onupdate=lambda: datetime.now(timezone.utc)
    )


class SearchHistory(Base):
    """SQLAlchemy SearchHistory model - user's search history"""
    __tablename__ = "search_history"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True
    )
    from_city: Mapped[str] = mapped_column(String(255), nullable=False)
    to_city: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Search parameters that were used
    from_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    from_lon: Mapped[Optional[float]] = mapped_column(nullable=True)
    to_lat: Mapped[Optional[float]] = mapped_column(nullable=True)
    to_lon: Mapped[Optional[float]] = mapped_column(nullable=True)
    date_from: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    date_to: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # Results count at the time of search
    results_count: Mapped[int] = mapped_column(nullable=False, default=0)
    
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )