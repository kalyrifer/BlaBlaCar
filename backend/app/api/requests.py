"""Requests endpoints"""
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel

from app.api.deps import get_current_user, get_request_service
from app.models.user import User
from app.services.request_service import RequestService, RequestNotFoundError, TripNotFoundError, ForbiddenError, NotEnoughSeatsError

router = APIRouter()


class UpdateRequestStatus(BaseModel):
    status: str


@router.get("/my")
async def get_my_requests(
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service)
):
    requests = await request_service.get_my_requests(current_user.id, status_filter)
    
    # Paginate
    total = len(requests)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_requests = requests[start:end]
    
    return {
        "items": paginated_requests,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size
    }


@router.put("/{request_id}")
async def update_request_status(
    request_id: str,
    request: UpdateRequestStatus,
    current_user: User = Depends(get_current_user),
    request_service: RequestService = Depends(get_request_service)
):
    try:
        result = await request_service.update_request_status(
            driver_id=current_user.id,
            request_id=UUID(request_id),
            new_status=request.status
        )
        return result
    except RequestNotFoundError:
        raise HTTPException(status_code=404, detail="Request not found")
    except TripNotFoundError:
        raise HTTPException(status_code=404, detail="Trip not found")
    except ForbiddenError:
        raise HTTPException(status_code=403, detail="Not authorized to update this request")
    except NotEnoughSeatsError:
        raise HTTPException(status_code=400, detail="Not enough available seats")
