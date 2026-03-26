"""Reviews API endpoints"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel, field_validator

from app.models.user import User
from app.services.review_service import ReviewService, get_review_service
from app.api.deps import get_current_user


router = APIRouter(prefix="/api/reviews", tags=["reviews"])


# ================== Request/Response DTOs ==================

class CreateReviewRequest(BaseModel):
    """Request DTO for creating a review"""
    trip_id: str
    reviewee_id: str
    review_type: str  # "driver_to_passenger" or "passenger_to_driver"
    accuracy_rating: int
    politeness_rating: int
    safety_rating: int
    text: str
    photo_urls: Optional[List[str]] = None
    
    @field_validator('accuracy_rating', 'politeness_rating', 'safety_rating')
    @classmethod
    def validate_rating(cls, v: int) -> int:
        if not 1 <= v <= 5:
            raise ValueError("Rating must be between 1 and 5")
        return v
    
    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        if len(v) < 50:
            raise ValueError("Review text must be at least 50 characters")
        return v


class ReviewResponse(BaseModel):
    """Response DTO for a review"""
    id: str
    trip_id: str
    reviewer_id: str
    reviewee_id: str
    review_type: str
    accuracy_rating: int
    politeness_rating: int
    safety_rating: int
    overall_rating: float
    text: str
    photo_urls: Optional[List[str]] = None
    is_verified: bool
    created_at: datetime


class UserRatingResponse(BaseModel):
    """Response DTO for user rating summary"""
    user_id: str
    average_rating: float
    total_reviews: int
    is_reliable_driver: bool
    is_reliable_passenger: bool
    avg_accuracy: float = 0.0
    avg_politeness: float = 0.0
    avg_safety: float = 0.0


# ================== API Endpoints ==================


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_review(
    request: CreateReviewRequest,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Create a new review for a trip.
    
    Can only leave a review within 14 days of trip completion.
    Minimum text length: 50 characters.
    """
    try:
        # Get trip completion date (would come from actual trip data)
        trip_completed_at = datetime.now(timezone.utc) - timedelta(days=1)
        
        review = await review_service.create_review(
            trip_id=UUID(request.trip_id),
            reviewer_id=current_user.id,
            reviewee_id=UUID(request.reviewee_id),
            review_type=request.review_type,
            accuracy_rating=request.accuracy_rating,
            politeness_rating=request.politeness_rating,
            safety_rating=request.safety_rating,
            text=request.text,
            trip_completed_at=trip_completed_at,
            photo_urls=request.photo_urls
        )
        
        return {
            "message": "Review created successfully",
            "review": {
                "id": str(review.id),
                "overall_rating": review.overall_rating
            }
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create review: {str(e)}"
        )


@router.get("/user/{user_id}/rating")
async def get_user_rating(
    user_id: str,
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Get user's rating summary including:
    - Average rating
    - Total reviews count
    - Badge status (reliable driver/passenger)
    """
    rating = await review_service.get_user_rating(UUID(user_id))
    return rating


@router.get("/user/{user_id}/reviews")
async def get_user_reviews(
    user_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    review_service: ReviewService = Depends(get_review_service)
):
    """Get reviews received by a user."""
    reviews = await review_service.get_user_reviews(
        user_id=UUID(user_id),
        limit=limit,
        offset=offset
    )
    
    return {
        "items": reviews,
        "total": len(reviews),
        "limit": limit,
        "offset": offset
    }


@router.get("/trip/{trip_id}/can-review")
async def check_can_review_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    review_service: ReviewService = Depends(get_review_service)
):
    """
    Check if current user can review a specific trip.
    Returns whether the review deadline has passed.
    """
    # In real implementation, get actual trip completion date
    trip_completed_at = datetime.now(timezone.utc) - timedelta(days=1)
    
    can_review, error = await review_service.can_review_trip(
        user_id=current_user.id,
        trip_id=UUID(trip_id),
        trip_completed_at=trip_completed_at
    )
    
    return {
        "can_review": can_review,
        "error": error,
        "deadline_days_remaining": 13  # Would be calculated
    }


@router.get("/trip/{trip_id}/reviews")
async def get_trip_reviews(
    trip_id: str,
    limit: int = Query(20, ge=1, le=100),
    review_service: ReviewService = Depends(get_review_service)
):
    """Get all reviews for a specific trip."""
    # In real implementation, fetch from repository
    return {
        "items": [],
        "total": 0
    }