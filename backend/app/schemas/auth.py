"""Auth Pydantic schemas (DTOs)"""
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator


# ================== Request DTOs ==================

class RegisterRequest(BaseModel):
    """Registration request DTO"""
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


class LoginRequest(BaseModel):
    """Login request DTO"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr
    password: str


# ================== Response DTOs ==================

class TokenResponse(BaseModel):
    """Token response DTO"""
    access_token: str
    token_type: str = "bearer"


class LogoutResponse(BaseModel):
    """Logout response DTO"""
    message: str = "Logged out"