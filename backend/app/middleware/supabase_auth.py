"""
Supabase JWT verification — used by /auth/supabase to bridge a Supabase sign-in
into our own JWT session.

Supabase issues JWTs signed with the project's JWT secret using HS256. After a
user signs in (OAuth, email, magic link), the frontend sends the Supabase
access token here; we verify it, find-or-create the matching local User row,
and the route hands back our own JWT for subsequent API calls.
"""

import logging
from dataclasses import dataclass

from fastapi import HTTPException, status
from jose import JWTError, jwt

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class SupabaseClaims:
    sub: str  # Supabase user UUID
    email: str
    role: str | None = None  # e.g. "authenticated"
    provider: str | None = None  # e.g. "google", "github", "email"
    full_name: str | None = None
    avatar_url: str | None = None


def verify_supabase_token(token: str) -> SupabaseClaims:
    """Verify a Supabase access token and extract user claims.

    Raises HTTPException(401) if the token is invalid, expired, or the
    backend isn't configured with a Supabase secret.
    """
    if not settings.supabase_jwt_secret:
        logger.error("SUPABASE_JWT_SECRET not configured — cannot verify token")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Supabase auth is not configured on this server",
        )

    try:
        # Supabase uses HS256 by default; audience is always "authenticated"
        payload = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated",
        )
    except JWTError as e:
        logger.info(f"Supabase token rejected: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase token",
        )

    sub = payload.get("sub")
    email = payload.get("email") or payload.get("user_metadata", {}).get("email")
    if not sub or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Supabase token missing required claims",
        )

    user_metadata = payload.get("user_metadata") or {}
    app_metadata = payload.get("app_metadata") or {}

    return SupabaseClaims(
        sub=sub,
        email=email,
        role=payload.get("role"),
        provider=app_metadata.get("provider"),
        full_name=user_metadata.get("full_name") or user_metadata.get("name"),
        avatar_url=user_metadata.get("avatar_url") or user_metadata.get("picture"),
    )
