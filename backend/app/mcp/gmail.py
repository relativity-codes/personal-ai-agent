from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings
from app.core.google_token import access_token_for_gmail
from app.mcp.base import MCPServer
from app.mcp.schema import MCPInvokeOAuth, ToolDefinition

logger = logging.getLogger(__name__)

GMAIL_THREADS_URL = "https://gmail.googleapis.com/gmail/v1/users/me/threads"


class GmailMCPServer(MCPServer):
    id = "gmail"
    display_name = "Gmail"
    description = "List threads using refresh token + client id/secret, or GMAIL_ACCESS_TOKEN."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _has_refresh_credentials(self) -> bool:
        return bool(
            self._settings.GOOGLE_CLIENT_ID
            and self._settings.GOOGLE_CLIENT_SECRET
            and (self._settings.GOOGLE_REFRESH_TOKEN or "").strip()
        )

    def _refresh_token(self, oauth: MCPInvokeOAuth | None) -> str:
        if oauth and (oauth.google_refresh_token or "").strip():
            return oauth.google_refresh_token.strip()
        return (self._settings.GOOGLE_REFRESH_TOKEN or "").strip()

    def _list_threads_ready(self, oauth: MCPInvokeOAuth | None) -> bool:
        if oauth and (oauth.gmail_access_token or "").strip():
            return True
        if (self._settings.GMAIL_ACCESS_TOKEN or "").strip():
            return True
        rt = self._refresh_token(oauth)
        return bool(
            self._settings.GOOGLE_CLIENT_ID
            and self._settings.GOOGLE_CLIENT_SECRET
            and rt
        )

    def _list_threads_invocation_allowed(self, oauth: MCPInvokeOAuth | None) -> bool:
        return self._list_threads_ready(oauth) or self.is_configured()

    def is_configured(self) -> bool:
        return bool(
            (self._settings.GMAIL_ACCESS_TOKEN or "").strip()
            or self._has_refresh_credentials()
            or (self._settings.GOOGLE_CLIENT_ID and self._settings.GOOGLE_CLIENT_SECRET)
        )

    async def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="list_threads",
                description="List recent threads (env tokens or invoke.oauth.google_refresh_token / gmail_access_token; Gmail scope in OAuth consent).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "default": "is:unread"},
                        "max_results": {"type": "integer", "default": 10},
                    },
                },
            ),
        ]

    async def invoke(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        oauth: MCPInvokeOAuth | None = None,
    ) -> dict[str, Any]:
        if tool_name != "list_threads":
            return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
        if not self._list_threads_invocation_allowed(oauth):
            return {
                "ok": False,
                "error": "not_configured",
                "message": (
                    "Set GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, and GOOGLE_REFRESH_TOKEN "
                    "(with Gmail scope), or set GMAIL_ACCESS_TOKEN. "
                    "You may also pass oauth.google_refresh_token or oauth.gmail_access_token on invoke."
                ),
            }
        token = await access_token_for_gmail(
            self._settings,
            gmail_access_token=oauth.gmail_access_token if oauth else None,
            refresh_token=oauth.google_refresh_token if oauth else None,
        )
        if not token:
            return {
                "ok": False,
                "error": "oauth_token_required",
                "message": (
                    "Could not obtain an access token. Add GOOGLE_REFRESH_TOKEN from OAuth consent "
                    "including Gmail scopes, or set GMAIL_ACCESS_TOKEN."
                ),
            }
        query = str(arguments.get("query", "is:unread"))
        max_results = min(max(int(arguments.get("max_results", 10)), 1), 100)
        headers = {"Authorization": f"Bearer {token}"}
        params = {"q": query, "maxResults": max_results}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                r = await client.get(GMAIL_THREADS_URL, headers=headers, params=params)
                r.raise_for_status()
                return {"ok": True, "data": r.json()}
        except httpx.HTTPStatusError as exc:
            logger.warning(
                "gmail http error: %s %s",
                exc.response.status_code,
                exc.response.text[:500],
            )
            return {
                "ok": False,
                "error": "upstream_error",
                "status_code": exc.response.status_code,
                "message": exc.response.text[:2000],
            }
        except httpx.RequestError as exc:
            logger.exception("gmail request failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}
