"""PostgreSQL Refresh Token Repository using SQLAlchemy"""
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_

from app.db.models.refresh_token import RefreshToken
from app.repositories.interfaces.refresh_token_repo import IRefreshTokenRepository


class PGRefreshTokenRepository(IRefreshTokenRepository):
    """PostgreSQL implementation of IRefreshTokenRepository"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, token_data: dict) -> RefreshToken:
        """Create new refresh token"""
        token = RefreshToken(**token_data)
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token
    
    async def get_by_token(self, token: str) -> Optional[RefreshToken]:
        """Get refresh token by token string"""
        stmt = select(RefreshToken).where(RefreshToken.token == token)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def validate(self, token: str) -> Optional[RefreshToken]:
        """Validate token and return if valid"""
        stmt = select(RefreshToken).where(
            and_(
                RefreshToken.token == token,
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.utcnow()
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def revoke(self, token: str) -> bool:
        """Revoke a refresh token"""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token == token)
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def revoke_by_hashed_token(self, hashed_token: str) -> bool:
        """Revoke a refresh token by hashed token"""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token == hashed_token)
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount > 0
    
    async def get_user_tokens(self, user_id: UUID) -> List[RefreshToken]:
        """Get all refresh tokens for a user"""
        stmt = select(RefreshToken).where(RefreshToken.user_id == user_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_all_tokens(self) -> List[RefreshToken]:
        """Get all refresh tokens (for admin/validation)"""
        stmt = select(RefreshToken).order_by(RefreshToken.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def revoke_all_for_user(self, user_id: UUID) -> int:
        """Revoke all tokens for a user"""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id)
            .values(is_revoked=True)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
    
    async def delete_expired(self) -> int:
        """Delete all expired tokens"""
        stmt = delete(RefreshToken).where(RefreshToken.expires_at < datetime.utcnow())
        result = await self.session.execute(stmt)
        await self.session.commit()
        return result.rowcount
