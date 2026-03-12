"""User Repository Interface"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.db.models.user import User


class IUserRepository(ABC):
    """Interface for User repository"""
    
    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def create(self, user_data: dict) -> User:
        """Create new user"""
        pass
    
    @abstractmethod
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update user"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        pass
    
    @abstractmethod
    async def list_all(self) -> List[User]:
        """List all users"""
        pass