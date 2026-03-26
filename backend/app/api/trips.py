"""Trips endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from app.api.deps import get_current_user, get_trip_service
from app.models.user import User
from app.services.trip_service import TripService, TripCreate, TripSearchFilters
from app.schemas.trip import TripAdvancedFilters
from app.core.exceptions import NotFoundError, ForbiddenError, NotEnoughSeatsError
from app.services.request_service import RequestService, UserAlreadyExistsError


# Re-export for backward compatibility
TripNotFoundError = NotFoundError
RequestNotFoundError = NotFoundError


router = APIRouter()


class CreateTripRequest(BaseModel):
    from_city: str
    to_city: str
    departure_at: str  # ISO datetime string
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None


class UpdateTripRequest(BaseModel):
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    departure_at: Optional[str] = None
    available_seats: Optional[int] = None
    price_per_seat: Optional[int] = None
    description: Optional[str] = None


@router.post("")
async def create_trip(
    request: CreateTripRequest,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    try:
        trip_create = TripCreate(
            from_city=request.from_city,
            to_city=request.to_city,
            departure_at=request.departure_at,
            available_seats=request.available_seats,
            price_per_seat=request.price_per_seat,
            description=request.description
        )
        result = await trip_service.create_trip(current_user.id, trip_create)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("")
async def list_trips(
    from_city: str = Query(..., description="Город отправления"),
    to_city: str = Query(..., description="Город прибытия"),
    date_from: Optional[str] = Query(None, description="Дата от (ISO datetime)"),
    date_to: Optional[str] = Query(None, description="Дата до (ISO datetime)"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    trip_service: TripService = Depends(get_trip_service)
):
    filters = TripSearchFilters(
        from_city=from_city,
        to_city=to_city,
        date_from=date_from,
        date_to=date_to
    )
    result = await trip_service.search_trips(filters, page, page_size)
    return result


@router.get("/my/driver")
async def get_my_trips_as_driver(
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    from app.core.database import get_db
    from app.models.request import RequestStatus
    
    trips = await trip_service.list_my_trips_as_driver(current_user.id)
    db = get_db()
    
    # Get passenger count for each trip
    result = []
    for trip in trips:
        trip_id = UUID(trip["id"])
        requests = await db.requests.get_by_trip(trip_id)
        confirmed_count = sum(
            1 for r in requests 
            if r.status == RequestStatus.CONFIRMED
        )
        trip["passengers_count"] = confirmed_count
        result.append(trip)
    
    return {
        "items": result,
        "total": len(result),
        "page": 1,
        "page_size": 20,
        "pages": 1
    }


@router.get("/{trip_id}")
async def get_trip(
    trip_id: str,
    trip_service: TripService = Depends(get_trip_service)
):
    trip = await trip_service.get_trip_by_id(UUID(trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@router.put("/{trip_id}")
async def update_trip(
    trip_id: str,
    request: UpdateTripRequest,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    update_data = request.model_dump(exclude_unset=True)
    result = await trip_service.update_trip(current_user.id, UUID(trip_id), update_data)
    return result


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    await trip_service.delete_or_cancel_trip(current_user.id, UUID(trip_id))
    return {"message": "Trip deleted"}


@router.post("/{trip_id}/requests")
async def create_request(
    trip_id: str,
    seats_requested: int = 1,
    message: str = None,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    from app.api.deps import get_request_service
    
    request_service: RequestService = await get_request_service()
    
    result = await request_service.create_request(
        passenger_id=current_user.id,
        trip_id=UUID(trip_id),
        seats=seats_requested,
        message=message
    )
    return result


@router.get("/{trip_id}/requests")
async def get_trip_requests(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    from app.api.deps import get_request_service
    
    request_service: RequestService = await get_request_service()
    
    result = await request_service.get_requests_by_trip(UUID(trip_id), current_user.id)
    return {
        "items": result,
        "total": len(result),
        "page": 1,
        "page_size": 20,
        "pages": 1
    }


# ================== Favorites and Subscriptions ==================


@router.post("/{trip_id}/favorite")
async def add_trip_to_favorites(
    trip_id: str,
    current_user: User = Depends(get_current_user)
):
    """Add a trip to user's favorites"""
    # In a real implementation, this would save to DB
    return {
        "message": "Trip added to favorites",
        "trip_id": trip_id,
        "user_id": str(current_user.id)
    }


@router.delete("/{trip_id}/favorite")
async def remove_trip_from_favorites(
    trip_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a trip from user's favorites"""
    return {
        "message": "Trip removed from favorites",
        "trip_id": trip_id
    }


@router.get("/favorites")
async def get_favorite_trips(
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    """Get user's favorite trips""
    # In a real implementation, this would fetch from DB
    return {
        "items": [],
        "total": 0,
        "page": 1,
        "page_size": 20,
        "pages": 1
    }


@router.get("/search/advanced")
async def advanced_trip_search(
    from_city: Optional[str] = Query(None),
    to_city: Optional[str] = Query(None),
    from_lat: Optional[float] = Query(None),
    from_lon: Optional[float] = Query(None),
    to_lat: Optional[float] = Query(None),
    to_lon: Optional[float] = Query(None),
    radius_km: int = Query(50, ge=1, le=200),
    date_from: Optional[str] = Query(None),
    date_to: Optional[str] = Query(None),
    departure_time_from: Optional[str] = Query(None),
    departure_time_to: Optional[str] = Query(None),
    available_seats_min: Optional[int] = Query(None, ge=1),
    price_min: Optional[int] = Query(None, ge=0),
    price_max: Optional[int] = Query(None, ge=0),
    car_type: Optional[str] = Query(None),
    smoking_allowed: Optional[bool] = Query(None),
    pets_allowed: Optional[bool] = Query(None),
    sort_by: str = Query("departure_at"),
    sort_order: str = Query("asc"),
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    """Advanced trip search with geolocation and filters"""
    from app.services.search_service import get_search_service
    
    search_service = await get_search_service()
    
    filters = TripAdvancedFilters(
        from_city=from_city,
        to_city=to_city,
        from_lat=from_lat,
        from_lon=from_lon,
        to_lat=to_lat,
        to_lon=to_lon,
        radius_km=radius_km,
        date_from=date_from,
        date_to=date_to,
        departure_time_from=departure_time_from,
        departure_time_to=departure_time_to,
        available_seats_min=available_seats_min,
        price_min=price_min,
        price_max=price_max,
        car_type=car_type,
        smoking_allowed=smoking_allowed,
        pets_allowed=pets_allowed,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    result = await search_service.search_trips_advanced(
        filters=filters,
        cursor=cursor,
        limit=limit
    )
    
    return result


@router.get("/{trip_id}/similar")
async def get_similar_trips(
    trip_id: str,
    limit: int = Query(5, ge=1, le=20)
):
    """Get similar trips to the given trip"""
    from app.services.search_service import get_search_service
    
    search_service = await get_search_service()
    
    similar_trips = await search_service.get_similar_trips(
        trip_id=UUID(trip_id),
        limit=limit
    )
    
    return {
        "items": similar_trips,
        "total": len(similar_trips)
    }


@router.get("/recommendations")
async def get_recommended_trips(
    current_user: User = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=50)
):
    """Get recommended trips based on user's history"""
    from app.services.search_service import get_search_service
    
    search_service = await get_search_service()
    
    recommended = await search_service.get_recommended_trips(
        user_id=current_user.id,
        limit=limit
    )
    
    return {
        "items": recommended,
        "total": len(recommended)
    }
