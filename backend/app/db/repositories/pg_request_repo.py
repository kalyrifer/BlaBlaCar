"""PostgreSQL Request Repository using SQLAlchemy"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.models.trip_request import TripRequest
from app.repositories.interfaces.request_repo import IRequestRepository


class PGRequestRepository(IRequestRepository):
    """PostgreSQL implementation of IRequestRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, request_id: UUID) -> Optional[TripRequest]:
        """Get request by ID"""
        stmt = select(TripRequest).where(TripRequest.id == request_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, request_data: dict) -> TripRequest:
        """Create new request"""
        request = TripRequest(**request_data)
        self.session.add(request)
        await self.session.commit()
        await self.session.refresh(request)
        return request
    
    async def update_status(self, request_id: UUID, status: str) -> Optional[TripRequest]:
        """Update request status"""
        request = await self.get_by_id(request_id)
        if request is None:
            return None
        
        request.status = status
        await self.session.commit()
        await self.session.refresh(request)
        return request
    
    async def list_by_trip(self, trip_id: UUID) -> List[TripRequest]:
        """List requests by trip"""
        stmt = select(TripRequest).where(TripRequest.trip_id == trip_id).order_by(TripRequest.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def list_by_passenger(self, passenger_id: UUID) -> List[TripRequest]:
        """List requests by passenger"""
        stmt = select(TripRequest).where(TripRequest.passenger_id == passenger_id).order_by(TripRequest.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def exists(self, trip_id: UUID, passenger_id: UUID) -> bool:
        """Check if request exists for trip and passenger"""
        stmt = select(TripRequest).where(
            and_(
                TripRequest.trip_id == trip_id,
                TripRequest.passenger_id == passenger_id
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none() is not None
