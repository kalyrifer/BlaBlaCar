"""In-memory RefreshToken Repository Implementation"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List
from uuid import UUID, uuid4

from app.repositories.interfaces.refresh_token_repo import IRefreshTokenRepository
from app.db.models.refresh_token import RefreshToken


@dataclass
class RefreshTokenData:
    """Internal data class for RefreshToken"""
    id: UUID
    user_id: UUID
    token: str
    expires_at: datetime
    is_revoked: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)


class InMemoryRefreshTokenRepository(IRefreshTokenRepository):
    """In-memory implementation of IRefreshTokenRepository"""
    
    def __init__(self):
        self._tokens: dict[UUID, RefreshTokenData] = {}
        self._token_to_id: dict[str, UUID] = {}  # Index for token lookup
    
    def _to_refresh_token_model(self, data: RefreshTokenData) -> RefreshToken:
        """Convert internal data to RefreshToken ORM model"""
        return RefreshToken(
            id=data.id,
            user_id=data.user_id,
            token=data.token,
            expires_at=data.expires_at,
            is_revoked=data.is_revoked,
            created_at=data.created_at
        )
    
    async def get_by_id(self, token_id: UUID) -> Optional[RefreshToken]:
        """Get refresh token by ID"""
        data = self._tokens.get(token_id)
        return self._to_refresh_token_model(data) if data else None
    
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        token_id = self._token_to_id.get(token)
        if not token_id:
            return None
        data = self._tokens.get(token_id)
        return self._to_refresh_token_model(data) if data else None
    
    async def create(self, token_data: dict) -> RefreshToken:
        """Create new refresh token"""
        token_id = uuid4()
        expires_at = datetime.utcnow() + timedelta(days=token_data.get("expires_in_days", 7))
        
        data = RefreshTokenData(
            id=token_id,
            user_id=token_data["user_id"],
            token=token_data["token"],
            expires_at=expires_at
        )
        self._tokens[token_id] = data
        self._token_to_id[token_data["token"]] = token_id
        return self._to_refresh_token_model(data)
    
    async def validate(self, token: str) -> Optional[RefreshToken]:
        """Validate token and return if valid"""
        token_data = await self.get_by_token(token)
        if not token_data:
            return None
        
        # Check if expired or revoked
        if token_data.is_revoked or token_data.expires_at < datetime.utcnow():
            return None
        
        return token_data
    
    async def revoke(self, token: str) -> bool:
        """Revoke a refresh token"""
        token_id = self._token_to_id.get(token)
        if not token_id:
            return False
        
        data = self._tokens.get(token_id)
        if not data:
            return False
        
        data.is_revoked = True
        return True
    
    async def get_user_tokens(self, user_id: UUID) -> List[RefreshToken]:
        """Get all refresh tokens for a user"""
        return [
            self._to_refresh_token_model(data)
            for data in self._tokens.values()
            if data.user_id == user_id
        ]
    
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all tokens for a user"""
        count = 0
        for data in self._tokens.values():
            if data.user_id == user_id and not data.is_revoked:
                data.is_revoked = True
                count += 1
        return count
    
    async def delete(self, token_id: UUID) -> bool:
        """Delete refresh token"""
        data = self._tokens.get(token_id)
        if not data:
            return False
        
        del self._token_to_id[data.token]
        del self._tokens[token_id]
        return True
    
    async def delete_expired(self) -> int:
        """Delete all expired tokens"""
        now = datetime.utcnow()
        expired_ids = [
            token_id for token_id, data in self._tokens.items()
            if data.expires_at < now
        ]
        
        for token_id in expired_ids:
            data = self._tokens[token_id]
            del self._token_to_id[data.token]
            del self._tokens[token_id]
        
        return len(expired_ids)