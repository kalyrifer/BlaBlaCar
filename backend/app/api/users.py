"""Users endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None


@router.get("/me")
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "rating": current_user.rating,
        "created_at": current_user.created_at.isoformat()
    }


@router.get("/{user_id}")
async def get_user(user_id: str, current_user: User = Depends(get_current_user)):
    db = get_db()
    
    user = await db.users.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get trip counts
    trips_as_driver = await db.trips.list_by_driver(user.id)
    
    # Count trips as passenger
    requests = await db.requests.get_by_passenger(user.id)
    trips_as_passenger = len([r for r in requests if r.status == "confirmed"])
    
    return {
        "id": str(user.id),
        "name": user.name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "rating": user.rating,
        "trips_as_driver": len(trips_as_driver),
        "trips_as_passenger": trips_as_passenger,
        "member_since": user.created_at.isoformat()
    }


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user)
):
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    db = get_db()
    
    update_data = request.model_dump(exclude_unset=True)
    updated_user = await db.users.update(UUID(user_id), update_data)
    
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": str(updated_user.id),
        "email": updated_user.email,
        "name": updated_user.name,
        "phone": updated_user.phone,
        "avatar_url": updated_user.avatar_url,
        "rating": updated_user.rating,
        "created_at": updated_user.created_at.isoformat()
    }


@router.get("/{user_id}/trips")
async def get_user_trips(
    user_id: str,
    role: Optional[str] = Query(None, description="driver or passenger"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100)
):
    db = get_db()
    
    user = await db.users.get_by_id(UUID(user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    result = []
    
    # Get trips as driver
    if role is None or role == "driver":
        trips_as_driver = await db.trips.list_by_driver(user.id)
        for trip in trips_as_driver:
            result.append({
                "id": str(trip.id),
                "role": "driver",
                "from_city": trip.from_city,
                "to_city": trip.to_city,
                "departure_date": trip.departure_date,
                "departure_time": trip.departure_time,
                "status": trip.status
            })
    
    # Get trips as passenger
    if role is None or role == "passenger":
        requests = await db.requests.get_by_passenger(user.id)
        for req in requests:
            if req.status == "confirmed":
                trip = await db.trips.get_by_id(req.trip_id)
                if trip:
                    result.append({
                        "id": str(trip.id),
                        "role": "passenger",
                        "from_city": trip.from_city,
                        "to_city": trip.to_city,
                        "departure_date": trip.departure_date,
                        "departure_time": trip.departure_time,
                        "status": trip.status
                    })
    
    # Paginate
    total = len(result)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_result = result[start:end]
    
    return {
        "items": paginated_result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }
