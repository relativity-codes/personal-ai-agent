import logging
from typing import Any
from urllib.parse import urlencode
import base64

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, parse_uuid
from app.config import settings
from app.core.google_token import GOOGLE_TOKEN_URL
from app.db.database import get_db
from app.db.repositories.mcp_credential_repository import MCPCredentialRepository
from app.api.schemas import MCPServiceId

logger = logging.getLogger(__name__)

router = APIRouter()

GOOGLE_AUTH_ENDPOINT = "https://accounts.google.com/o/oauth2/v2/auth"
GITHUB_AUTH_ENDPOINT = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
NOTION_AUTH_ENDPOINT = "https://api.notion.com/v1/oauth/authorize"
NOTION_TOKEN_URL = "https://api.notion.com/v1/oauth/token"


@router.get("/oauth/status")
def mcp_oauth_status(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    """Non-secret view of how MCP auth can be satisfied."""
    return {
        "google": {
            "oauth_client_configured": bool(settings.GOOGLE_CLIENT_ID and settings.GOOGLE_CLIENT_SECRET),
            "authorize_url_path": "/api/v1/mcp/oauth/google/authorize-url",
            "token_exchange_path": "/api/v1/mcp/oauth/google/token",
        },
        "github": {
            "oauth_client_configured": bool(settings.GITHUB_CLIENT_ID and settings.GITHUB_CLIENT_SECRET),
            "authorize_url_path": "/api/v1/mcp/oauth/github/authorize-url",
            "token_exchange_path": "/api/v1/mcp/oauth/github/token",
        },
        "notion": {
            "oauth_client_configured": bool(settings.NOTION_CLIENT_ID and settings.NOTION_CLIENT_SECRET),
            "authorize_url_path": "/api/v1/mcp/oauth/notion/authorize-url",
            "token_exchange_path": "/api/v1/mcp/oauth/notion/token",
        },
    }


@router.get("/oauth/google/authorize-url")
def google_oauth_authorize_url(
    user: dict = Depends(get_current_user),
    redirect_uri: str = Query(..., description="Must match a redirect URI allowed for this Google OAuth client."),
    state: str = Query(None, description="Optional state parameter to pass through to the callback."),
) -> dict[str, str]:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="GOOGLE_CLIENT_ID is not configured.")
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": (settings.GOOGLE_OAUTH_SCOPES or "").strip(),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    if state:
        params["state"] = state
    return {"url": f"{GOOGLE_AUTH_ENDPOINT}?{urlencode(params)}"}


class OAuthTokenRequest(BaseModel):
    code: str = Field(..., min_length=1)
    redirect_uri: str = Field(..., min_length=8)


@router.post("/oauth/google/token")
async def google_oauth_exchange(
    body: OAuthTokenRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Exchange code for Google tokens and store in MCPCredential."""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Google OAuth not configured.")
    
    uid = parse_uuid(user["user_id"], "user_id")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(GOOGLE_TOKEN_URL, data={
            "code": body.code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": body.redirect_uri,
            "grant_type": "authorization_code",
        })
        if not r.is_success:
            raise HTTPException(status_code=400, detail=r.text)
        data = r.json()

    # Store in MCPCredential
    creds = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "refresh_token": data.get("refresh_token"),
        "access_token": data.get("access_token"),
    }
    
    existing = await MCPCredentialRepository.get_by_user_and_server(db, uid, MCPServiceId.GOOGLE)
    if existing:
        await MCPCredentialRepository.update(db, existing.id, creds)
    else:
        await MCPCredentialRepository.create(db, uid, MCPServiceId.GOOGLE, creds)
    
    await db.commit()
    return {"ok": True, "message": "Google credentials stored."}


@router.get("/oauth/github/authorize-url")
def github_oauth_authorize_url(
    user: dict = Depends(get_current_user),
    redirect_uri: str = Query(..., description="Must match GitHub redirect URI."),
    state: str = Query(None, description="Optional state parameter."),
) -> dict[str, str]:
    if not settings.GITHUB_CLIENT_ID:
        raise HTTPException(status_code=503, detail="GITHUB_CLIENT_ID is not configured.")
    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "scope": "repo user",
    }
    if state:
        params["state"] = state
    return {"url": f"{GITHUB_AUTH_ENDPOINT}?{urlencode(params)}"}


@router.post("/oauth/github/token")
async def github_oauth_exchange(
    body: OAuthTokenRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Exchange code for GitHub token and store in MCPCredential."""
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="GitHub OAuth not configured.")
    
    uid = parse_uuid(user["user_id"], "user_id")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(GITHUB_TOKEN_URL, data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": body.code,
            "redirect_uri": body.redirect_uri,
        }, headers={"Accept": "application/json"})
        if not r.is_success:
            raise HTTPException(status_code=400, detail=r.text)
        data = r.json()

    # Store in MCPCredential
    creds = {"token": data.get("access_token")}
    
    existing = await MCPCredentialRepository.get_by_user_and_server(db, uid, MCPServiceId.GITHUB)
    if existing:
        await MCPCredentialRepository.update(db, existing.id, creds)
    else:
        await MCPCredentialRepository.create(db, uid, MCPServiceId.GITHUB, creds)
    
    await db.commit()
    return {"ok": True, "message": "GitHub credentials stored."}


@router.get("/oauth/notion/authorize-url")
def notion_oauth_authorize_url(
    user: dict = Depends(get_current_user),
    redirect_uri: str = Query(..., description="Must match Notion redirect URI."),
    state: str = Query(None, description="Optional state parameter."),
) -> dict[str, str]:
    if not settings.NOTION_CLIENT_ID:
        raise HTTPException(status_code=503, detail="NOTION_CLIENT_ID is not configured.")
    params = {
        "client_id": settings.NOTION_CLIENT_ID,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "owner": "user",
    }
    if state:
        params["state"] = state
    return {"url": f"{NOTION_AUTH_ENDPOINT}?{urlencode(params)}"}


@router.post("/oauth/notion/token")
async def notion_oauth_exchange(
    body: OAuthTokenRequest,
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user),
) -> dict[str, Any]:
    """Exchange code for Notion token and store in MCPCredential."""
    if not settings.NOTION_CLIENT_ID or not settings.NOTION_CLIENT_SECRET:
        raise HTTPException(status_code=503, detail="Notion OAuth not configured.")
    
    uid = parse_uuid(user["user_id"], "user_id")
    
    auth_header = base64.b64encode(f"{settings.NOTION_CLIENT_ID}:{settings.NOTION_CLIENT_SECRET}".encode()).decode()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        r = await client.post(NOTION_TOKEN_URL, json={
            "grant_type": "authorization_code",
            "code": body.code,
            "redirect_uri": body.redirect_uri,
        }, headers={
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        })
        if not r.is_success:
            raise HTTPException(status_code=400, detail=r.text)
        data = r.json()

    # Store in MCPCredential
    creds = {
        "token": data.get("access_token"),
        "workspace_id": data.get("workspace_id"),
        "workspace_name": data.get("workspace_name"),
    }
    
    existing = await MCPCredentialRepository.get_by_user_and_server(db, uid, MCPServiceId.NOTION)
    if existing:
        await MCPCredentialRepository.update(db, existing.id, creds)
    else:
        await MCPCredentialRepository.create(db, uid, MCPServiceId.NOTION, creds)
    
    await db.commit()
    return {"ok": True, "message": "Notion credentials stored."}
