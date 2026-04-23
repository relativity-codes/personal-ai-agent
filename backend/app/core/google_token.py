from __future__ import annotations

import logging

import httpx

from app.config import Settings

logger = logging.getLogger(__name__)

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


async def exchange_refresh_token(
    settings: Settings,
    *,
    refresh_token: str | None = None,
) -> str | None:
    cid = settings.GOOGLE_CLIENT_ID
    sec = settings.GOOGLE_CLIENT_SECRET
    refresh = (refresh_token or settings.GOOGLE_REFRESH_TOKEN or "").strip()
    if not cid or not sec or not refresh:
        return None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": cid,
                    "client_secret": sec,
                    "refresh_token": refresh,
                    "grant_type": "refresh_token",
                },
            )
            r.raise_for_status()
            data = r.json()
            token = data.get("access_token")
            if not token or not isinstance(token, str):
                logger.warning("google token response missing access_token")
                return None
            return token
    except httpx.HTTPStatusError as exc:
        logger.warning(
            "google oauth token error: %s %s",
            exc.response.status_code,
            exc.response.text[:500],
        )
        return None
    except httpx.RequestError as exc:
        logger.exception("google oauth token request failed: %s", exc)
        return None


async def access_token_for_calendar(
    settings: Settings,
    *,
    calendar_access_token: str | None = None,
    refresh_token: str | None = None,
) -> str | None:
    direct = (calendar_access_token or settings.GOOGLE_CALENDAR_ACCESS_TOKEN or "").strip()
    if direct:
        return direct
    return await exchange_refresh_token(settings, refresh_token=refresh_token)


async def access_token_for_gmail(
    settings: Settings,
    *,
    gmail_access_token: str | None = None,
    refresh_token: str | None = None,
) -> str | None:
    direct = (gmail_access_token or settings.GMAIL_ACCESS_TOKEN or "").strip()
    if direct:
        return direct
    return await exchange_refresh_token(settings, refresh_token=refresh_token)
