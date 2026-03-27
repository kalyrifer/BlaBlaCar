"""User Pydantic schemas (DTOs)"""
from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


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
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate that phone number starts with +375 (Belarus)"""
        if not v.startswith('+375'):
            raise ValueError('Номер телефона должен начинаться с +375 (например, +375291234567)')
        return v


class UserCreateInternal(BaseModel):
    """Internal Create DTO (used by services, without password)"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr
    password_hash: str
    name: str
    phone: str
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate that phone number starts with +375 (Belarus)"""
        if not v.startswith('+375'):
            raise ValueError('Номер телефона должен начинаться с +375 (например, +375291234567)')
        return v


# ================== Update DTOs ==================

class UserUpdate(BaseModel):
    """Update DTO for User"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    
    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        """Validate that phone number starts with +375 (Belarus)"""
        if v is not None and not v.startswith('+375'):
            raise ValueError('Номер телефона должен начинаться с +375 (например, +375291234567)')
        return v


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