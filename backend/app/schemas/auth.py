"""Auth Pydantic schemas (DTOs)"""
from pydantic import BaseModel, EmailStr, ConfigDict


# ================== Request DTOs ==================

class RegisterRequest(BaseModel):
    """Registration request DTO"""
    model_config = ConfigDict(str_strip_whitespace=True)
    
    email: EmailStr
    password: str
    name: str
    phone: str


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