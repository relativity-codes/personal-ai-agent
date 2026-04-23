from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.deps import get_current_user
from app.config import settings
from app.core.google_token import GOOGLE_TOKEN_URL

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"


@router.get("/oauth/status")
def mcp_oauth_status(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    """Non-secret view of how MCP auth can be satisfied (env vs invoke body)."""
    return {
        "google": {
            "oauth_client_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
            "env_refresh_configured": bool((settings.GOOGLE_REFRESH_TOKEN or "").strip()),
            "authorize_url_path": "/api/v1/mcp/oauth/google/authorize-url",
            "token_exchange_path": "/api/v1/mcp/oauth/google/token",
            "invoke_oauth_fields": [
                "google_refresh_token",
                "google_calendar_access_token",
                "gmail_access_token",
            ],
        },
        "github": {"invoke_oauth_fields": ["github_token"]},
        "notion": {"invoke_oauth_fields": ["notion_token"]},
    }


@router.get("/oauth/google/authorize-url")
def google_oauth_authorize_url(
    user: dict = Depends(get_current_user),
    redirect_uri: str = Query(
        ...,
        min_length=8,
        description="Must match a redirect URI allowed for this Google OAuth client.",
    ),
) -> dict[str, str]:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="GOOGLE_CLIENT_ID is not configured.")
    scopes = (settings.GOOGLE_OAUTH_SCOPES or "").strip()
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": scopes,
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    url = f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"
    return {"url": url}


class GoogleOAuthTokenRequest(BaseModel):
    code: str = Field(..., min_length=1)
    redirect_uri: str = Field(..., min_length=8)


@router.post("/oauth/google/token")
async def google_oauth_exchange(
    body: GoogleOAuthTokenRequest,
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Exchange an authorization code for tokens (store refresh_token securely; wire to invoke.oauth later)."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET must be set for token exchange.",
        )
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": body.code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": body.redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as exc:
        logger.warning("google oauth code exchange failed: %s", exc.response.text[:500])
        raise HTTPException(
            status_code=400,
            detail=exc.response.text[:2000],
        ) from exc
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "access_token": data.get("access_token"),
        "expires_in": data.get("expires_in"),
        "refresh_token": data.get("refresh_token"),
        "scope": data.get("scope"),
        "token_type": data.get("token_type"),
    }
