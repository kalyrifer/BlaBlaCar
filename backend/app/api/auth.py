"""Auth endpoints"""
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr

from app.api.deps import get_current_user, get_auth_service
from app.services.auth_service import AuthService, UserCreate
from app.models.user import User

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
async def register(request: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        user_create = UserCreate(
            email=request.email,
            password=request.password,
            name=request.name,
            phone=request.phone
        )
        result = await auth_service.register(user_create)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login")
async def login(request: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    try:
        result = await auth_service.login(request.email, request.password)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


@router.post("/logout")
async def logout():
    # JWT tokens are stateless, logout is handled on client side
    return {"message": "Logged out"}


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "phone": current_user.phone,
        "avatar_url": current_user.avatar_url,
        "rating": current_user.rating,
        "created_at": current_user.created_at.isoformat()
    }
