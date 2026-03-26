"""
Review service for managing ratings and reviews.
"""
import logging
from datetime import datetime, timezone
from typing import Optional, List
from uuid import UUID

from app.db.models.review import Review, UserRatingSummary, ReviewValidation

logger = logging.getLogger(__name__)


class ReviewService:
    """
    Service for creating and managing reviews.
    """
    
    def __init__(self, session=None):
        self.session = session
    
    async def create_review(
        self,
        trip_id: UUID,
        reviewer_id: UUID,
        reviewee_id: UUID,
        review_type: str,
        accuracy_rating: int,
        politeness_rating: int,
        safety_rating: int,
        text: str,
        trip_completed_at: datetime,
        photo_urls: Optional[List[str]] = None
    ) -> Review:
        """
        Create a new review.
        
        Args:
            trip_id: Trip ID being reviewed
            reviewer_id: User leaving the review
            reviewee_id: User receiving the review
            review_type: "driver_to_passenger" or "passenger_to_driver"
            accuracy_rating: 1-5 rating for accuracy
            politeness_rating: 1-5 rating for politeness
            safety_rating: 1-5 rating for safety
            text: Review text (min 50 chars)
            trip_completed_at: When the trip was completed
            photo_urls: Optional list of photo URLs
            
        Returns:
            Created Review object
            
        Raises:
            ValueError: If validation fails
        """
        # Validate ratings
        for rating in [accuracy_rating, politeness_rating, safety_rating]:
            if not ReviewValidation.validate_rating(rating):
                raise ValueError("Ratings must be between 1 and 5")
        
        # Validate text
        is_valid, error = ReviewValidation.validate_text(text)
        if not is_valid:
            raise ValueError(error)
        
        # Check if within review deadline
        can_review, error = ReviewValidation.can_leave_review(trip_completed_at)
        if not can_review:
            raise ValueError(error)
        
        # Calculate overall rating
        overall = ReviewValidation.calculate_overall_rating(
            accuracy_rating, politeness_rating, safety_rating
        )
        
        # Create review (simplified - in real implementation would save to DB)
        review = Review(
            trip_id=trip_id,
            reviewer_id=reviewer_id,
            reviewee_id=reviewee_id,
            review_type=review_type,
            accuracy_rating=accuracy_rating,
            politeness_rating=politeness_rating,
            safety_rating=safety_rating,
            overall_rating=overall,
            text=text,
            photo_urls=",".join(photo_urls) if photo_urls else None,
            is_verified=True  # In real impl, verify trip completion
        )
        
        # Update user rating summary
        await self._update_user_rating_summary(reviewee_id, review_type)
        
        logger.info(f"Review created for user {reviewee_id} with rating {overall}")
        return review
    
    async def _update_user_rating_summary(
        self, 
        user_id: UUID, 
        review_type: str
    ) -> None:
        """
        Update the user's rating summary after a new review.
        
        In a real implementation, this would:
        1. Fetch all reviews for the user
        2. Calculate new averages
        3. Update or create UserRatingSummary record
        """
        # Simplified implementation
        # In production, this would be a database operation
        logger.info(f"Updating rating summary for user {user_id}")
    
    async def get_user_rating(self, user_id: UUID) -> dict:
        """
        Get user's rating summary.
        
        Returns:
            Dictionary with rating info and badges
        """
        # In real implementation, fetch from UserRatingSummary
        return {
            "user_id": str(user_id),
            "average_rating": 0.0,
            "total_reviews": 0,
            "is_reliable_driver": False,
            "is_reliable_passenger": False
        }
    
    async def get_user_reviews(
        self, 
        user_id: UUID, 
        limit: int = 20,
        offset: int = 0
    ) -> List[dict]:
        """
        Get user's received reviews.
        
        Args:
            user_id: User ID
            limit: Number of reviews to return
            offset: Offset for pagination
            
        Returns:
            List of review dictionaries
        """
        # In real implementation, fetch from Review table
        return []
    
    async def can_review_trip(
        self,
        user_id: UUID,
        trip_id: UUID,
        trip_completed_at: datetime
    ) -> tuple[bool, Optional[str]]:
        """
        Check if user can review a specific trip.
        
        Returns:
            Tuple of (can_review, error_message)
        """
        # Check if already reviewed
        # In real implementation, check if review exists
        
        # Check deadline
        return ReviewValidation.can_leave_review(trip_completed_at)


async def get_review_service() -> ReviewService:
    """Get ReviewService instance."""
    return ReviewService()