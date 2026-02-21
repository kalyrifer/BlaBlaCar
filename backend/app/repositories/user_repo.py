"""In-memory User Repository"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime

from app.models.user import User
from app.repositories.interfaces import IUserRepository


class InMemoryUserRepository(IUserRepository):
    """In-memory реализация UserRepository"""
    
    def __init__(self):
        self._users: dict[UUID, User] = {}
        self._email_index: dict[str, UUID] = {}
    
    async def create(self, user_data: dict) -> User:
        user_id = uuid4()
        user = User(
            id=user_id,
            email=user_data["email"],
            password_hash=user_data["password_hash"],
            name=user_data["name"],
            phone=user_data.get("phone"),
            avatar_url=user_data.get("avatar_url"),
            rating=user_data.get("rating"),
            created_at=datetime.utcnow()
        )
        self._users[user_id] = user
        self._email_index[user.email] = user_id
        return user
    
    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        return self._users.get(user_id)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        user_id = self._email_index.get(email)
        return self._users.get(user_id) if user_id else None
    
    async def update(self, user_id: UUID, user_data: dict) -> Optional[User]:
        if user_id not in self._users:
            return None
        user = self._users[user_id]
        for key, value in user_data.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        return user
    
    async def delete(self, user_id: UUID) -> bool:
        if user_id not in self._users:
            return False
        user = self._users.pop(user_id)
        self._email_index.pop(user.email, None)
        return True
    
    async def list_all(self) -> List[User]:
        return list(self._users.values())
