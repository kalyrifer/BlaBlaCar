"""Requests endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.request import RequestStatus
from app.models.trip import TripStatus

router = APIRouter()


class UpdateRequestStatus(BaseModel):
    status: str


@router.get("/my")
async def get_my_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    requests = await db.requests.get_by_passenger(current_user.id)
    
    # Filter by status if provided
    if status_filter:
        requests = [r for r in requests if r.status == status_filter]
    
    # Paginate
    total = len(requests)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_requests = requests[start:end]
    
    result = []
    for req in paginated_requests:
        trip = await db.trips.get_by_id(req.trip_id)
        driver = await db.users.get_by_id(trip.driver_id) if trip else None
        
        result.append({
            "id": str(req.id),
            "trip_id": str(req.trip_id),
            "trip": {
                "id": str(trip.id),
                "from_city": trip.from_city,
                "to_city": trip.to_city,
                "departure_date": trip.departure_date,
                "departure_time": trip.departure_time,
                "driver_name": driver.name if driver else None
            } if trip else None,
            "seats_requested": req.seats_requested,
            "status": req.status,
            "created_at": req.created_at.isoformat()
        })
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.put("/{request_id}")
async def update_request_status(
    request_id: str,
    request: UpdateRequestStatus,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    req = await db.requests.get_by_id(UUID(request_id))
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
    
    trip = await db.trips.get_by_id(req.trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Only trip owner can update status
    if trip.driver_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this request")
    
    # Update status
    updated_req = await db.requests.update_status(UUID(request_id), request.status)
    
    # Create notification for passenger
    if request.status == RequestStatus.CONFIRMED:
        notification_type = "request_confirmed"
        notification_title = "Заявка подтверждена"
        notification_message = "Водитель подтвердил вашу заявку на поездку"
    else:
        notification_type = "request_rejected"
        notification_title = "Заявка отклонена"
        notification_message = "Водитель отклонил вашу заявку на поездку"
    
    await db.notifications.create({
        "user_id": req.passenger_id,
        "type": notification_type,
        "title": notification_title,
        "message": notification_message,
        "related_trip_id": req.trip_id,
        "related_request_id": req.id
    })
    
    # Update available seats if confirmed
    if request.status == RequestStatus.CONFIRMED:
        await db.trips.update_seats(req.trip_id, -req.seats_requested)
    
    return {
        "id": str(updated_req.id),
        "trip_id": str(updated_req.trip_id),
        "passenger_id": str(updated_req.passenger_id),
        "seats_requested": updated_req.seats_requested,
        "status": updated_req.status,
        "created_at": updated_req.created_at.isoformat(),
        "updated_at": updated_req.updated_at.isoformat() if updated_req.updated_at else None
    }
