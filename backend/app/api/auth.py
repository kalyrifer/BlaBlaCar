"""Auth endpoints"""
from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel, EmailStr

from app.api.deps import get_current_user, get_auth_service, get_refresh_token_repo
from app.services.auth_service import AuthService, UserCreate
from app.repositories.interfaces import IRefreshTokenRepository
from app.models.user import User
from app.core.security import create_access_token, create_refresh_token
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError

router = APIRouter()


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str
    phone: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


@router.post("/register")
async def register(
    request: RegisterRequest, 
    auth_service: AuthService = Depends(get_auth_service),
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repo)
):
    user_create = UserCreate(
        email=request.email,
        password=request.password,
        name=request.name,
        phone=request.phone
    )
    result = await auth_service.register(user_create)
    
    # Also generate token for the newly registered user
    access_token = create_access_token({"sub": str(result.id)}, exp_minutes=15)
    
    # Generate refresh token
    raw_token, hashed_token = create_refresh_token(result.id)
    
    # Store hashed token
    await refresh_token_repo.create({
        "user_id": UUID(result.id),
        "hashed_token": hashed_token,
        "expires_in_days": 7
    })
    
    return {
        "access_token": access_token,
        "refresh_token": raw_token,
        "token_type": "bearer",
        "user": result
    }


@router.post("/login")
async def login(
    request: LoginRequest, 
    auth_service: AuthService = Depends(get_auth_service),
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repo)
):
    result = await auth_service.login(request.email, request.password)
    
    # Generate refresh token
    raw_token, hashed_token = create_refresh_token(result.user.id)
    
    # Store hashed token
    await refresh_token_repo.create({
        "user_id": UUID(result.user.id),
        "hashed_token": hashed_token,
        "expires_in_days": 7
    })
    
    return {
        "access_token": result.access_token,
        "refresh_token": raw_token,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repo)
):
    """Refresh access token using refresh token"""
    # Validate the refresh token
    token_data = await refresh_token_repo.validate(request.refresh_token)
    
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    # Create new access token
    access_token = create_access_token({"sub": str(token_data.user_id)}, exp_minutes=15)
    
    # Rotate refresh token - invalidate old, create new
    # First, get the hashed token from the validated token data
    # We need to find and revoke it
    user_tokens = await refresh_token_repo.get_user_tokens(token_data.user_id)
    
    # Find the token that matches (the one we just validated)
    for token in user_tokens:
        # Check if this is the token we validated (non-revoked, non-expired)
        if not token.is_revoked and token.expires_at.replace(tzinfo=None) > datetime.utcnow():
            await refresh_token_repo.revoke_by_hashed_token(token.token)
            break
    
    # Create new refresh token
    raw_token, hashed_token = create_refresh_token(token_data.user_id)
    await refresh_token_repo.create({
        "user_id": token_data.user_id,
        "hashed_token": hashed_token,
        "expires_in_days": 7
    })
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_token,
        token_type="bearer"
    )


@router.post("/logout")
async def logout(
    request: RefreshRequest,
    current_user: User = Depends(get_current_user),
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repo)
):
    """Logout - revoke the provided refresh token"""
    # Validate the token first
    token_data = await refresh_token_repo.validate(request.refresh_token)
    
    if not token_data or token_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Refresh token not found"
        )
    
    # Revoke the token
    await refresh_token_repo.revoke_by_hashed_token(token_data.token)
    
    return {"message": "Logged out successfully"}


@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    refresh_token_repo: IRefreshTokenRepository = Depends(get_refresh_token_repo)
):
    """Logout from all devices - revoke all refresh tokens for the user"""
    count = await refresh_token_repo.revoke_all_for_user(current_user.id)
    return {"message": f"Logged out from {count} device(s)"}


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
