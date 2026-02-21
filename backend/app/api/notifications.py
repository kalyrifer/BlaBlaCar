"""Notifications endpoints"""
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Query
from pydantic import BaseModel

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("")
async def get_notifications(
    is_read: Optional[bool] = Query(None, description="Filter by read status"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    notifications = await db.notifications.get_by_user(current_user.id, is_read)
    
    # Paginate
    total = len(notifications)
    start = (page - 1) * page_size
    end = start + page_size
    paginated_notifications = notifications[start:end]
    
    result = []
    for notif in paginated_notifications:
        result.append({
            "id": str(notif.id),
            "type": notif.type,
            "title": notif.title,
            "message": notif.message,
            "is_read": notif.is_read,
            "related_trip_id": str(notif.related_trip_id) if notif.related_trip_id else None,
            "related_request_id": str(notif.related_request_id) if notif.related_request_id else None,
            "created_at": notif.created_at.isoformat()
        })
    
    # Get unread count
    unread_count = await db.notifications.get_unread_count(current_user.id)
    
    return {
        "items": result,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": (total + page_size - 1) // page_size,
        "unread_count": unread_count
    }


@router.put("/{notification_id}/read")
async def mark_notification_as_read(
    notification_id: str,
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    notification = await db.notifications.mark_as_read(
        UUID_from_str(notification_id)
    )
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    return {
        "id": str(notification.id),
        "type": notification.type,
        "title": notification.title,
        "message": notification.message,
        "is_read": notification.is_read,
        "related_trip_id": str(notification.related_trip_id) if notification.related_trip_id else None,
        "created_at": notification.created_at.isoformat()
    }


@router.put("/read-all")
async def mark_all_notifications_as_read(
    current_user: User = Depends(get_current_user)
):
    db = get_db()
    
    count = await db.notifications.mark_all_as_read(current_user.id)
    
    return {"message": f"Marked {count} notifications as read"}


def UUID_from_str(s: str):
    """Helper to convert string to UUID"""
    from uuid import UUID
    return UUID(s)
