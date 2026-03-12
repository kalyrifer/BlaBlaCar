"""Trips endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from app.api.deps import get_current_user, get_trip_service
from app.models.user import User
from app.services.trip_service import TripService, TripCreate, TripSearchFilters, TripNotFoundError, ForbiddenError

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
    try:
        update_data = request.model_dump(exclude_unset=True)
        result = await trip_service.update_trip(current_user.id, UUID(trip_id), update_data)
        return result
    except TripNotFoundError:
        raise HTTPException(status_code=404, detail="Trip not found")
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    try:
        await trip_service.delete_or_cancel_trip(current_user.id, UUID(trip_id))
        return {"message": "Trip deleted"}
    except TripNotFoundError:
        raise HTTPException(status_code=404, detail="Trip not found")
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/{trip_id}/requests")
async def create_request(
    trip_id: str,
    seats_requested: int = 1,
    message: str = None,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    from app.services.request_service import RequestService, RequestNotFoundError, ForbiddenError, NotEnoughSeatsError, RequestAlreadyExistsError
    from app.api.deps import get_request_service
    
    request_service: RequestService = await get_request_service()
    
    try:
        result = await request_service.create_request(
            passenger_id=current_user.id,
            trip_id=UUID(trip_id),
            seats=seats_requested,
            message=message
        )
        return result
    except RequestNotFoundError:
        raise HTTPException(status_code=404, detail="Trip not found")
    except (ForbiddenError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotEnoughSeatsError:
        raise HTTPException(status_code=400, detail="Not enough available seats")
    except RequestAlreadyExistsError:
        raise HTTPException(status_code=409, detail="Request already sent")


@router.get("/{trip_id}/requests")
async def get_trip_requests(
    trip_id: str,
    current_user: User = Depends(get_current_user),
    trip_service: TripService = Depends(get_trip_service)
):
    from app.api.deps import get_request_service
    from app.services.request_service import RequestService, TripNotFoundError, ForbiddenError
    
    request_service: RequestService = await get_request_service()
    
    try:
        result = await request_service.get_requests_by_trip(UUID(trip_id), current_user.id)
        return {
            "items": result,
            "total": len(result),
            "page": 1,
            "page_size": 20,
            "pages": 1
        }
    except TripNotFoundError:
        raise HTTPException(status_code=404, detail="Trip not found")
    except ForbiddenError as e:
        raise HTTPException(status_code=403, detail=str(e))
