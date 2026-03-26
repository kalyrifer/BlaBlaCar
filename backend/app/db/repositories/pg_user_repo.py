"""PostgreSQL User Repository using SQLAlchemy"""
from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import UUID as PGUUID

from app.db.models.user import User
from app.repositories.interfaces.user_repo import IUserRepository


class PGUserRepository(IUserRepository):
    """PostgreSQL implementation of IUserRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, user_data: dict) -> User:
        """Create new user"""
        user = User(**user_data)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update user"""
        user = await self.get_by_id(user_id)
        if user is None:
            return None
        
        for key, value in user_data.items():
            setattr(user, key, value)
        
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        user = await self.get_by_id(user_id)
        if user is None:
            return False
        
        await self.session.delete(user)
        await self.session.commit()
        return True
    
    async def list_all(self) -> List[User]:
        """List all users"""
        stmt = select(User)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
