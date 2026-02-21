"""Domain model - User"""
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime
from typing import Optional


class User(BaseModel):
    """User domain model"""
    id: UUID
    email: EmailStr
    password_hash: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(BaseModel):
    """User model for internal use"""
    id: UUID
    email: EmailStr
    password_hash: str
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
