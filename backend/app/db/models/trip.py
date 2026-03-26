"""SQLAlchemy Trip ORM model"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.models.base import Base


class Trip(Base):
    """SQLAlchemy Trip model"""
    __tablename__ = "trips"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    driver_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True
    )
    from_city: Mapped[str] = mapped_column(String(255), nullable=False)
    to_city: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Geolocation fields (optional for now, required in future)
    from_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    from_lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    to_lat: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    to_lon: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # Search radius in kilometers
    search_radius_km: Mapped[int] = mapped_column(Integer, nullable=False, default=50)
    
    departure_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False
    )
    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_seat: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Additional filters
    car_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    luggage_size: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    smoking_allowed: Mapped[bool] = mapped_column(nullable=False, default=False)
    pets_allowed: Mapped[bool] = mapped_column(nullable=False, default=False)
    
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="active", index=True)
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
