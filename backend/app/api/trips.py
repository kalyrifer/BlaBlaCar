"""Trips endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.models.user import User
from app.models.trip import Trip
from app.models.request import RequestStatus
from app.repositories.request_repo import InMemoryRequestRepository

router = APIRouter()


class CreateTripRequest(BaseModel):
    from_city: str
    to_city: str
    departure_date: str
    departure_time: str
    available_seats: int
    price_per_seat: int
    description: Optional[str] = None


class UpdateTripRequest(BaseModel):
    from_city: Optional[str] = None
    to_city: Optional[str] = None
    departure_date: Optional[str] = None
    departure_time: Optional[str] = None
    available_seats: Optional[int] = None
    price_per_seat: Optional[int] = None
    description: Optional[str] = None


@router.post("")
async def create_trip(
    request: CreateTripRequest,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    trip = await db.trips.create({
        "driver_id": current_user.id,
        "from_city": request.from_city,
        "to_city": request.to_city,
        "departure_date": request.departure_date,
        "departure_time": request.departure_time,
        "available_seats": request.available_seats,
        "price_per_seat": request.price_per_seat,
        "description": request.description,
        "status": "active"
    })
    
    return {
        "id": str(trip.id),
        "driver_id": str(trip.driver_id),
        "from_city": trip.from_city,
        "to_city": trip.to_city,
        "departure_date": trip.departure_date,
        "departure_time": trip.departure_time,
        "available_seats": trip.available_seats,
        "price_per_seat": trip.price_per_seat,
        "description": trip.description,
        "status": trip.status,
        "created_at": trip.created_at.isoformat()
    }


@router.get("")
async def list_trips(
    from_city: str = Query(..., description="Город отправления"),
    to_city: str = Query(..., description="Город прибытия"),
    date: Optional[str] = Query(None, description="Дата поездки YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    db = get_db()
    
    trips = await db.trips.list_by_filters(from_city, to_city, date, "active")
    
    # Paginate
    total = len(trips)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_trips = trips[start:end]
    
    # Get driver info for each trip
    result = []
    for trip in paginated_trips:
        driver = await db.users.get_by_id(trip.driver_id)
        result.append({
            "id": str(trip.id),
            "driver_id": str(trip.driver_id),
            "driver": {
                "id": str(driver.id),
                "name": driver.name,
                "avatar_url": driver.avatar_url,
                "rating": driver.rating
            } if driver else None,
            "from_city": trip.from_city,
            "to_city": trip.to_city,
            "departure_date": trip.departure_date,
            "departure_time": trip.departure_time,
            "available_seats": trip.available_seats,
            "price_per_seat": trip.price_per_seat,
            "status": trip.status
        })
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.get("/my/driver")
async def get_my_trips_as_driver(
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    trips = await db.trips.list_by_driver(current_user.id)
    result = []
    
    for trip in trips:
        # Count passengers
        requests = await db.requests.get_by_trip(trip.id)
        confirmed_count = sum(
            1 for r in requests 
            if r.status == RequestStatus.CONFIRMED
        )
        
        result.append({
            "id": str(trip.id),
            "from_city": trip.from_city,
            "to_city": trip.to_city,
            "departure_date": trip.departure_date,
            "departure_time": trip.departure_time,
            "available_seats": trip.available_seats,
            "price_per_seat": trip.price_per_seat,
            "status": trip.status,
            "passengers_count": confirmed_count
        })
    
    return {
        "items": result,
        "total": len(result),
        "page": 1,
        "page_size": 20,
        "pages": 1
    }


@router.get("/{trip_id}")
async def get_trip(trip_id: str):
    db = get_db()
    
    trip = await db.trips.get_by_id(UUID(trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    driver = await db.users.get_by_id(trip.driver_id)
    
    return {
        "id": str(trip.id),
        "driver_id": str(trip.driver_id),
        "driver": {
            "id": str(driver.id),
            "name": driver.name,
            "phone": driver.phone,
            "avatar_url": driver.avatar_url,
            "rating": driver.rating,
            "created_at": driver.created_at.isoformat()
        } if driver else None,
        "from_city": trip.from_city,
        "to_city": trip.to_city,
        "departure_date": trip.departure_date,
        "departure_time": trip.departure_time,
        "available_seats": trip.available_seats,
        "price_per_seat": trip.price_per_seat,
        "description": trip.description,
        "status": trip.status,
        "created_at": trip.created_at.isoformat()
    }


@router.put("/{trip_id}")
async def update_trip(
    trip_id: str,
    request: UpdateTripRequest,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    trip = await db.trips.get_by_id(UUID(trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the owner of this trip")
    
    update_data = request.model_dump(exclude_unset=True)
    updated_trip = await db.trips.update(UUID(trip_id), update_data)
    
    return {
        "id": str(updated_trip.id),
        "driver_id": str(updated_trip.driver_id),
        "from_city": updated_trip.from_city,
        "to_city": updated_trip.to_city,
        "departure_date": updated_trip.departure_date,
        "departure_time": updated_trip.departure_time,
        "available_seats": updated_trip.available_seats,
        "price_per_seat": updated_trip.price_per_seat,
        "description": updated_trip.description,
        "status": updated_trip.status,
        "created_at": updated_trip.created_at.isoformat()
    }


@router.delete("/{trip_id}")
async def delete_trip(
    trip_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    trip = await db.trips.get_by_id(UUID(trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the owner of this trip")
    
    await db.trips.delete(UUID(trip_id))
    return {"message": "Trip deleted"}


@router.post("/{trip_id}/requests")
async def create_request(
    trip_id: str,
    seats_requested: int = 1,
    message: str = None,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    trip = await db.trips.get_by_id(UUID(trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot request your own trip")
    
    # Check if already requested
    exists = await db.requests.exists(UUID(trip_id), current_user.id)
    if exists:
        raise HTTPException(status_code=409, detail="Request already sent")
    
    request = await db.requests.create({
        "trip_id": UUID(trip_id),
        "passenger_id": current_user.id,
        "seats_requested": seats_requested,
        "message": message,
        "status": "pending"
    })
    
    # Create notification for driver
    await db.notifications.create({
        "user_id": trip.driver_id,
        "type": "request_received",
        "title": "Новая заявка",
        "message": f"Пользователь {current_user.name} отправил заявку на вашу поездку",
        "related_trip_id": UUID(trip_id),
        "related_request_id": request.id
    })
    
    return {
        "id": str(request.id),
        "trip_id": str(request.trip_id),
        "passenger_id": str(request.passenger_id),
        "seats_requested": request.seats_requested,
        "message": request.message,
        "status": request.status,
        "created_at": request.created_at.isoformat()
    }


@router.get("/{trip_id}/requests")
async def get_trip_requests(
    trip_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    trip = await db.trips.get_by_id(UUID(trip_id))
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    if trip.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not the owner of this trip")
    
    requests = await db.requests.get_by_trip(UUID(trip_id))
    result = []
    
    for req in requests:
        passenger = await db.users.get_by_id(req.passenger_id)
        result.append({
            "id": str(req.id),
            "passenger_id": str(req.passenger_id),
            "passenger": {
                "id": str(passenger.id),
                "name": passenger.name,
                "avatar_url": passenger.avatar_url,
                "rating": passenger.rating,
                "phone": passenger.phone
            } if passenger else None,
            "seats_requested": req.seats_requested,
            "message": req.message,
            "status": req.status,
            "created_at": req.created_at.isoformat()
        })
    
    return {
        "items": result,
        "total": len(result),
        "page": 1,
        "page_size": 20,
        "pages": 1
    }
