"""User Pydantic schemas (DTOs)"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict


# ================== Response DTOs ==================

class UserResponse(BaseModel):
    """Response DTO for User"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: EmailStr
    name: str
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    created_at: datetime


class UserShortResponse(BaseModel):
    """Short response DTO for User (used in nested responses)"""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    avatar_url: Optional[str] = None
    rating: Optional[float] = None
    phone: Optional[str] = None


# ================== Create DTOs ==================

class UserCreate(BaseModel):
    """Create DTO for User registration"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr
    password: str
    name: str
    phone: str


class UserCreateInternal(BaseModel):
    """Internal Create DTO (used by services, without password)"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr
    password_hash: str
    name: str
    phone: str


# ================== Update DTOs ==================

class UserUpdate(BaseModel):
    """Update DTO for User"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None


# ================== Login DTOs ==================

class UserLoginRequest(BaseModel):
    """Login request DTO"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Login response DTO"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse