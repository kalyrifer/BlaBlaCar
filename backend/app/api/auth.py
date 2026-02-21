"""Auth endpoints"""
from fastapi import APIRouter, HTTPException, status, Response
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user
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


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    phone: str
    avatar_url: str | None = None
    rating: float | None = None


@router.post("/register")
async def register(request: RegisterRequest):
    db = get_db()
    
    # Check if email already exists
    existing = await db.users.get_by_email(request.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    user = await db.users.create({
        "email": request.email,
        "password_hash": get_password_hash(request.password),
        "name": request.name,
        "phone": request.phone
    })
    
    # Generate token
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name
    })
    
    return {
        "id": str(user.id),
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "avatar_url": user.avatar_url,
        "rating": user.rating,
        "created_at": user.created_at.isoformat()
    }


@router.post("/login")
async def login(request: LoginRequest, response: Response):
    db = get_db()
    
    user = await db.users.get_by_email(request.email)
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "name": user.name
    })
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "name": user.name,
            "phone": user.phone,
            "avatar_url": user.avatar_url,
            "rating": user.rating
        }
    }


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
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
