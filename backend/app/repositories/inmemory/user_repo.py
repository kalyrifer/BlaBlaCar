"""In-memory User Repository Implementation"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4

from app.repositories.interfaces.user_repo import IUserRepository
from app.db.models.user import User


@dataclass
class UserData:
    """Internal data class for User"""
    id: UUID
    email: str
    password_hash: str
    name: str
    phone: str
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None


class InMemoryUserRepository(IUserRepository):
    """In-memory implementation of IUserRepository"""
    
    def __init__(self):
        self._users: dict[UUID, UserData] = {}
    
    def _to_user_model(self, data: UserData) -> User:
        """Convert internal data to User ORM model"""
        return User(
            id=data.id,
            email=data.email,
            password_hash=data.password_hash,
            name=data.name,
            phone=data.phone,
            avatar_url=data.avatar_url,
            rating=data.rating,
            created_at=data.created_at
        )
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID"""
        data = self._users.get(user_id)
        return self._to_user_model(data) if data else None
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        for data in self._users.values():
            if data.email == email:
                return self._to_user_model(data)
        return None
    
    async def create(self, user_data: dict) -> User:
        """Create new user"""
        user_id = uuid4()
        data = UserData(
            id=user_id,
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            name=user_data["name"],
            phone=user_data["phone"],
            avatar_url=user_data.get("avatar_url"),
            rating=user_data.get("rating")
        )
        self._users[user_id] = data
        return self._to_user_model(data)
    
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        """Update user"""
        data = self._users.get(user_id)
        if not data:
            return None
        
        for key, value in user_data.items():
            if hasattr(data, key):
                setattr(data, key, value)
        
        data.updated_at = datetime.utcnow()
        return self._to_user_model(data)
    
    async def delete(self, user_id: UUID) -> bool:
        """Delete user"""
        if user_id in self._users:
            del self._users[user_id]
            return True
        return False
    
    async def list_all(self) -> List[User]:
        """List all users"""
        return [self._to_user_model(data) for data in self._users.values()]