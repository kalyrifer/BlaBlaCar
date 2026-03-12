"""Refresh Token Repository Interface"""
from abc import ABC, abstractmethod
from typing import Optional, List
from uuid import UUID

from app.db.models.refresh_token import RefreshToken


class IRefreshTokenRepository(ABC):
    """Interface for RefreshToken repository"""
    
    @abstractmethod
    async def create(self, token_data: dict) -> RefreshToken:
        """Create new refresh token"""
        pass
    
    @abstractmethod
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        pass
    
    @abstractmethod
    async def validate(self, token: str) -> Optional[RefreshToken]:
        """Validate token and return if valid"""
        pass
    
    @abstractmethod
    async def revoke(self, token: str) -> bool:
        """Revoke a refresh token"""
        pass
    
    @abstractmethod
    async def revoke_by_hashed_token(self, hashed_token: str) -> bool:
        """Revoke a refresh token by hashed token"""
        pass
    
    @abstractmethod
    async def get_user_tokens(self, user_id: UUID) -> List[RefreshToken]:
        """Get all refresh tokens for a user"""
        pass
    
    @abstractmethod
    async def get_all_tokens(self) -> List[RefreshToken]:
        """Get all refresh tokens (for admin/validation)"""
        pass
    
    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all tokens for a user"""
        pass
    
    @abstractmethod
    async def delete_expired(self) -> int:
        """Delete all expired tokens"""
        pass