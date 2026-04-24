from __future__ import annotations

import logging
import jwt
from typing import Annotated, TypedDict

from fastapi import Depends, Header, HTTPException, Request
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
    google_id: str
    email: str
    name: str | None
    avatar_url: str | None


async def get_current_user(
    request: Request,
    authorization: Annotated[str | None, Header(alias="Authorization")] = None,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)] = None,
    db: AsyncSession = Depends(get_session),
) -> CurrentUser:

    # 1. Try to get from Cookie first
    raw = request.cookies.get("access_token")
    
    # 2. Fallback to Authorization Header
    if not raw:
        raw = parse_bearer_token(authorization) or (creds.credentials if creds else None)
    
    if not raw:
        raise HTTPException(status_code=401, detail="Missing authentication token")

    try:
        payload = jwt.decode(
            raw, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token: missing sub")
    except Exception as exc:
        logger.debug("jwt verify failed: %s", exc)
        raise HTTPException(status_code=401, detail="Invalid or expired session token") from exc

    user = await UserRepository.get_by_id(db, parse_uuid(user_id))
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
        
    return {
        "user_id": str(user.id),
        "google_id": user.google_id or "none",
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

# Alias for compatibility with existing imports
from app.db.session import get_session as get_db
