import re
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, Token
from app.middleware.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    get_current_user,
)
from app.middleware.rate_limit import limiter
from app.middleware.supabase_auth import verify_supabase_token
from pydantic import BaseModel, EmailStr, Field

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    refresh_token: str


class SupabaseLoginRequest(BaseModel):
    access_token: str = Field(min_length=10)


async def _unique_username(db: AsyncSession, base: str) -> str:
    """Find a free username starting from `base`. Appends -2, -3, ... on collision."""
    base = re.sub(r"[^a-zA-Z0-9_-]", "", base).lower()[:40] or "user"
    candidate = base
    n = 2
    while True:
        existing = await db.execute(select(User).where(User.username == candidate))
        if not existing.scalar_one_or_none():
            return candidate
        candidate = f"{base}-{n}"[:50]
        n += 1
        if n > 999:
            return f"{base}-{uuid.uuid4().hex[:6]}"


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def register(request: Request, data: UserCreate, db: AsyncSession = Depends(get_db)):
    # Check existing
    existing = await db.execute(
        select(User).where((User.email == data.email) | (User.username == data.username))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or username already exists")

    user = User(
        email=data.email,
        username=data.username,
        hashed_password=hash_password(data.password),
        full_name=data.full_name,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


@router.post("/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, data: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    return Token(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.post("/supabase", response_model=Token)
@limiter.limit("20/minute")
async def supabase_login(request: Request, data: SupabaseLoginRequest, db: AsyncSession = Depends(get_db)):
    """Exchange a Supabase access token for our own JWT.

    Frontend flow: after `supabase.auth.signInWith*` succeeds, POST the
    resulting `access_token` here. We verify it, find-or-create the local
    User row, and return access + refresh tokens the same shape as /login.
    """
    claims = verify_supabase_token(data.access_token)

    # Find existing user — prefer supabase_user_id match, fall back to email
    result = await db.execute(
        select(User).where(User.supabase_user_id == claims.sub)
    )
    user = result.scalar_one_or_none()

    if not user:
        # Maybe they registered earlier via email/password and now signed in via OAuth
        result = await db.execute(select(User).where(User.email == claims.email))
        user = result.scalar_one_or_none()
        if user:
            # Link the existing local account to this Supabase identity
            user.supabase_user_id = claims.sub
            if claims.provider and not user.auth_provider:
                user.auth_provider = claims.provider
            if claims.avatar_url and not user.avatar_url:
                user.avatar_url = claims.avatar_url

    if not user:
        # Create a fresh account
        username_base = claims.email.split("@", 1)[0]
        username = await _unique_username(db, username_base)
        user = User(
            email=claims.email,
            username=username,
            full_name=claims.full_name or username,
            hashed_password=None,
            is_verified=True,  # Supabase verified the email
            avatar_url=claims.avatar_url,
            supabase_user_id=claims.sub,
            auth_provider=claims.provider or "supabase",
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")

    return Token(
        access_token=create_access_token(str(user.id), user.role.value),
        refresh_token=create_refresh_token(str(user.id)),
    )


@router.get("/me", response_model=UserRead)
async def get_me(user: User = Depends(get_current_user)):
    return user
