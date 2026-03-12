"""SQLAlchemy Trip ORM model"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey
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
    departure_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False
    )
    available_seats: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_seat: Mapped[int] = mapped_column(Integer, nullable=False)
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
