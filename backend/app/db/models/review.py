"""SQLAlchemy Review ORM model for ratings and feedback"""
from datetime import datetime, timezone, timedelta
from typing import Optional
from uuid import UUID, uuid4
from sqlalchemy import String, Integer, DateTime, ForeignKey, Boolean, Text, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.models.base import Base

# Constants
REVIEW_MIN_TEXT_LENGTH = 50
REVIEW_DEADLINE_DAYS = 14
RELIABLE_RATING_THRESHOLD = 4.5


class Review(Base):
    """SQLAlchemy Review model for trip ratings and feedback"""
    __tablename__ = "reviews"
    
    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4
    )
    
    # Review relationships
    trip_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("trips.id"), 
        nullable=False,
        index=True
    )
    reviewer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True
    )
    reviewee_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"), 
        nullable=False,
        index=True
    )
    
    # Review type: driver reviewing passenger, or passenger reviewing driver
    review_type: Mapped[str] = mapped_column(String(20), nullable=False)  # "driver_to_passenger" or "passenger_to_driver"
    
    # Ratings (1-5 stars each)
    accuracy_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # Description accuracy
    politeness_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # Friendliness
    safety_rating: Mapped[int] = mapped_column(Integer, nullable=False)  # Safety
    overall_rating: Mapped[float] = mapped_column(Float, nullable=False)  # Calculated average
    
    # Text review (minimum 50 characters)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Photo reviews (optional) - stored as JSON array of URLs
    photo_urls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Review status
    is_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # Verified trip completion
    is_hidden: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)  # Hidden by moderation
    
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


class UserRatingSummary(Base):
    """Aggregated rating summary for users (denormalized for performance)"""
    __tablename__ = "user_rating_summaries"
    
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), 
        ForeignKey("users.id"), 
        primary_key=True
    )
    
    # Aggregated metrics
    average_rating: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_reviews: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    
    # Individual rating averages
    avg_accuracy: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_politeness: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    avg_safety: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    
    # Badge status
    is_reliable_driver: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_reliable_passenger: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    
    # Last updated
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        nullable=False, 
        default=lambda: datetime.now(timezone.utc)
    )


class ReviewValidation:
    """Business logic for review validation"""
    
    @staticmethod
    def can_leave_review(trip_completed_at: datetime) -> tuple[bool, Optional[str]]:
        """
        Check if user can still leave a review for a completed trip.
        Reviews must be left within 14 days of trip completion.
        
        Returns:
            Tuple of (can_leave_review, error_message)
        """
        deadline = trip_completed_at + timedelta(days=REVIEW_DEADLINE_DAYS)
        now = datetime.now(timezone.utc)
        
        if now > deadline:
            return False, f"Review deadline has passed. You can only review within {REVIEW_DEADLINE_DAYS} days of trip completion."
        
        return True, None
    
    @staticmethod
    def validate_rating(rating: int) -> bool:
        """Validate that rating is between 1 and 5."""
        return 1 <= rating <= 5
    
    @staticmethod
    def validate_text(text: str) -> tuple[bool, Optional[str]]:
        """Validate review text meets minimum length requirement."""
        if len(text) < REVIEW_MIN_TEXT_LENGTH:
            return False, f"Review text must be at least {REVIEW_MIN_TEXT_LENGTH} characters."
        return True, None
    
    @staticmethod
    def calculate_overall_rating(accuracy: int, politeness: int, safety: int) -> float:
        """Calculate overall rating as weighted average."""
        # Weights: accuracy 30%, politeness 30%, safety 40%
        return (accuracy * 0.3 + politeness * 0.3 + safety * 0.4)
    
    @staticmethod
    def should_get_badge(average_rating: float) -> bool:
        """Check if user qualifies for reliable badge (4.5+ rating)."""
        return average_rating >= RELIABLE_RATING_THRESHOLD