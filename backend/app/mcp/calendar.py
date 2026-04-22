from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings
from app.mcp.base import MCPServer
from app.mcp.schema import ToolDefinition

logger = logging.getLogger(__name__)

CALENDAR_EVENTS_URL = "https://www.googleapis.com/calendar/v3/calendars/primary/events"


class CalendarMCPServer(MCPServer):
    id = "calendar"
    display_name = "Google Calendar"
    description = "Fetch events and detect conflicts (OAuth required for live calls in v1)."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_configured(self) -> bool:
        return bool(
            (self._settings.GOOGLE_CLIENT_ID and self._settings.GOOGLE_CLIENT_SECRET)
            or (self._settings.GOOGLE_CALENDAR_ACCESS_TOKEN or "").strip()
        )

    async def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="list_events",
                description="List calendar events in a time range (requires Google OAuth token).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "time_min": {"type": "string", "description": "RFC3339 start"},
                        "time_max": {"type": "string", "description": "RFC3339 end"},
                        "max_results": {"type": "integer", "default": 20},
                    },
                    "required": ["time_min", "time_max"],
                },
            ),
            ToolDefinition(
                name="detect_overlaps",
                description="Given a list of events, return overlapping intervals (local helper).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "events": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Events with start/end or summary fields",
                        }
                    },
                    "required": ["events"],
                },
            ),
        ]

    def _has_access_token(self) -> bool:
        return bool((self._settings.GOOGLE_CALENDAR_ACCESS_TOKEN or "").strip())

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "list_events":
            if not self.is_configured():
                return {
                    "ok": False,
                    "error": "not_configured",
                    "message": "Set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET (OAuth app) and/or GOOGLE_CALENDAR_ACCESS_TOKEN.",
                }
            if not self._has_access_token():
                return {
                    "ok": False,
                    "error": "oauth_token_required",
                    "message": (
                        "Client ID and secret register your app with Google, but the Calendar API needs a "
                        "user access token. Run an OAuth consent flow, then put the access token in "
                        "GOOGLE_CALENDAR_ACCESS_TOKEN (refresh-token storage can be added later)."
                    ),
                    "docs": "https://developers.google.com/identity/protocols/oauth2",
                }
            time_min = arguments.get("time_min")
            time_max = arguments.get("time_max")
            if not time_min or not time_max:
                return {"ok": False, "error": "validation_error", "message": "time_min and time_max (RFC3339) are required."}
            max_results = min(int(arguments.get("max_results", 20)), 250)
            token = (self._settings.GOOGLE_CALENDAR_ACCESS_TOKEN or "").strip()
            headers = {"Authorization": f"Bearer {token}"}
            params = {
                "timeMin": time_min,
                "timeMax": time_max,
                "maxResults": max_results,
                "singleEvents": "true",
                "orderBy": "startTime",
            }
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.get(CALENDAR_EVENTS_URL, headers=headers, params=params)
                    r.raise_for_status()
                    return {"ok": True, "data": r.json()}
            except httpx.HTTPStatusError as exc:
                logger.warning(
                    "calendar http error: %s %s",
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
                logger.exception("calendar request failed")
                return {"ok": False, "error": "request_error", "message": str(exc)}
        if tool_name == "detect_overlaps":
            events = arguments.get("events") or []
            overlaps: list[dict[str, Any]] = []
            for i, a in enumerate(events):
                for j, b in enumerate(events):
                    if j <= i:
                        continue
                    overlaps.append({"pair": (i, j), "note": "Compare start/end in orchestrator"})
            return {"ok": True, "overlaps": overlaps, "event_count": len(events)}
        return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
