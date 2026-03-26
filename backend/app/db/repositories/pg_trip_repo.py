"""PostgreSQL Trip Repository using SQLAlchemy"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import selectinload

from app.db.models.trip import Trip
from app.repositories.interfaces.trip_repo import ITripRepository


class PGTripRepository(ITripRepository):
    """PostgreSQL implementation of ITripRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, trip_id: UUID) -> Optional[Trip]:
        """Get trip by ID"""
        stmt = select(Trip).where(Trip.id == trip_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def search(
        self, 
        from_city: str, 
        to_city: str, 
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        status: str = "active"
    ) -> List[Trip]:
        """Search trips by filters"""
        conditions = [
            Trip.from_city.ilike(f"%{from_city}%"),
            Trip.to_city.ilike(f"%{to_city}%"),
            Trip.status == status
        ]
        
        if date_from:
            conditions.append(Trip.departure_at >= date_from)
        if date_to:
            conditions.append(Trip.departure_at <= date_to)
        
        stmt = select(Trip).where(and_(*conditions)).order_by(Trip.departure_at)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def create(self, trip_data: dict) -> Trip:
        """Create new trip"""
        trip = Trip(**trip_data)
        self.session.add(trip)
        await self.session.commit()
        await self.session.refresh(trip)
        return trip
    
    async def update(self, trip_id: UUID, trip_data: dict) -> Optional[Trip]:
        """Update trip"""
        trip = await self.get_by_id(trip_id)
        if trip is None:
            return None
        
        for key, value in trip_data.items():
            setattr(trip, key, value)
        
        await self.session.commit()
        await self.session.refresh(trip)
        return trip
    
    async def delete(self, trip_id: UUID) -> bool:
        """Delete trip"""
        trip = await self.get_by_id(trip_id)
        if trip is None:
            return False
        
        await self.session.delete(trip)
        await self.session.commit()
        return True
    
    async def list_by_driver(self, driver_id: UUID) -> List[Trip]:
        """List trips by driver"""
        stmt = select(Trip).where(Trip.driver_id == driver_id).order_by(Trip.departure_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update_seats(self, trip_id: UUID, seats_delta: int) -> Optional[Trip]:
        """Update available seats (add/subtract)"""
        trip = await self.get_by_id(trip_id)
        if trip is None:
            return None
        
        trip.available_seats += seats_delta
        await self.session.commit()
        await self.session.refresh(trip)
        return trip
    
    async def lock_for_update(self, trip_id: UUID) -> Optional[Trip]:
        """Lock trip for update and return current state"""
        stmt = select(Trip).where(Trip.id == trip_id).with_for_update()
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
