"""
Auth Router — /api/auth/*
Handles: register, login, me, logout
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from api.database import get_db
from api.db_models import User
from api.schemas import UserCreate, UserLogin, Token, UserResponse
from api.auth import (
    verify_password, get_password_hash,
    create_access_token, require_auth
)
from api.config import settings

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
db_router = APIRouter(prefix="/api/db/auth", tags=["Authentication (Legacy)"])


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
@db_router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user account"""
    # Check duplicate username
    existing = await db.execute(select(User).where(User.username == user_data.username))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")

    # Check duplicate email
    existing_email = await db.execute(select(User).where(User.email == user_data.email))
    if existing_email.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password)
    )
    db.add(user)
    await db.flush()

    token = create_access_token(
        {"sub": str(user.id), "username": user.username},
        timedelta(minutes=settings.access_token_expire_minutes)
    )
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=Token)
@db_router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with username and password"""
    result = await db.execute(select(User).where(User.username == credentials.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")

    token = create_access_token(
        {"sub": str(user.id), "username": user.username},
        timedelta(minutes=settings.access_token_expire_minutes)
    )
    return Token(access_token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
@db_router.get("/verify", response_model=UserResponse)
@db_router.post("/verify", response_model=UserResponse)
async def get_me(current_user: User = Depends(require_auth)):
    """Get current user profile"""
    return current_user
