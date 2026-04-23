from __future__ import annotations

import logging
from typing import Annotated, TypedDict

from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core import security
from app.db.repositories.user_repository import UserRepository
from app.db.session import async_session_factory, get_session
from app.utils.validators import parse_bearer_token, parse_uuid

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser(TypedDict, total=False):
    """Authenticated principal for API routes and agent state."""

    user_id: str
    clerk_sub: str
    email: str
    name: str | None
    avatar_url: str | None


async def get_current_user(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> CurrentUser:
    if settings.DEV_AUTH_BYPASS:
        return {
            "user_id": settings.DEV_USER_INTERNAL_ID,
            "clerk_sub": "dev_bypass",
            "email": "dev@localhost",
            "name": "Dev User",
            "avatar_url": None,
        }

    raw = parse_bearer_token(authorization) or (creds.credentials if creds else None)
    if not raw:
        raise HTTPException(status_code=401, detail="Missing bearer token")

    if not settings.CLERK_ISSUER.strip():
        raise HTTPException(
            status_code=503,
            detail="Server auth misconfigured: set CLERK_ISSUER or enable DEV_AUTH_BYPASS",
        )

    try:
        claims = security.decode_clerk_session_token(raw)
    except Exception as exc:
        logger.debug("jwt verify failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired session token") from exc

    profile = security.claims_to_profile(claims)
    clerk_sub = profile["clerk_sub"]
    if not clerk_sub:
        raise HTTPException(status_code=401, detail="Token missing subject")

    async with async_session_factory() as session:
        user = await UserRepository.get_by_clerk_id(session, clerk_sub)
        if user is None:
            user = await UserRepository.upsert_from_clerk(
                session,
                clerk_id=clerk_sub,
                email=profile.get("email") or "unknown@users.clerk",
                name=profile.get("name"),
                avatar_url=profile.get("avatar_url"),
            )
        await session.commit()
        return {
            "user_id": str(user.id),
            "clerk_sub": clerk_sub,
            "email": user.email,
            "name": user.name,
            "avatar_url": user.avatar_url,
        }


async def get_current_user_optional(
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
) -> CurrentUser | None:
    try:
        return await get_current_user(authorization=authorization, creds=creds)
    except HTTPException as exc:
        if exc.status_code == 401:
            return None
        raise


SessionDep = Annotated[AsyncSession, Depends(get_session)]
