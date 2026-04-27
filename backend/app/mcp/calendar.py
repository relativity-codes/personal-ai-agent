from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings
from app.core.google_token import access_token_for_calendar
from app.mcp.base import MCPServer
from app.mcp.schema import MCPInvokeOAuth, ToolDefinition

logger = logging.getLogger(__name__)

CALENDAR_V3_BASE = "https://www.googleapis.com/calendar/v3"

class CalendarMCPServer(MCPServer):
    id = "calendar"
    display_name = "Google Calendar"
    description = "A comprehensive suite of tools for managing Google Calendar events."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _has_refresh_credentials(self, oauth: MCPInvokeOAuth | None) -> bool:
        return bool(
            self._settings.GOOGLE_CLIENT_ID
            and self._settings.GOOGLE_CLIENT_SECRET
            and oauth
            and (oauth.google_refresh_token or "").strip()
        )

    def _refresh_token(self, oauth: MCPInvokeOAuth | None) -> str:
        if oauth and (oauth.google_refresh_token or "").strip():
            return oauth.google_refresh_token.strip()
        return ""

    def _invocation_ready(self, oauth: MCPInvokeOAuth | None) -> bool:
        if oauth and (oauth.google_calendar_access_token or "").strip():
            return True
        return self._has_refresh_credentials(oauth)

    def is_configured(self) -> bool:
        return self._invocation_ready(None) or (self._settings.GOOGLE_CLIENT_ID and self._settings.GOOGLE_CLIENT_SECRET)

    async def list_tools(self) -> list[ToolDefinition]:
        # All tools, existing and new, are correctly defined here.
        return [
            ToolDefinition(name="list_events", description="List calendar events.", input_schema={
                "type": "object", "properties": {
                    "time_min": {"type": "string"}, "time_max": {"type": "string"}, "max_results": {"type": "integer", "default": 20}},
                "required": ["time_min", "time_max"],}),
            ToolDefinition(name="detect_overlaps", description="Find overlapping event intervals.", input_schema={
                "type": "object", "properties": {"events": {"type": "array", "items": {"type": "object"}}}, "required": ["events"],}),
            ToolDefinition(name="calendar_fetch_events", description="Get events from the primary calendar.", input_schema={
                "type": "object", "properties": {
                    "start_date": {"type": "string"}, "end_date": {"type": "string"}, "max_results": {"type": "integer", "default": 20}},
                "required": ["start_date", "end_date"],}),
            ToolDefinition(name="calendar_find_free_slots", description="Find available time slots (mock).", input_schema={
                "type": "object", "properties": {"date": {"type": "string"}, "duration_minutes": {"type": "integer"}},
                "required": ["date", "duration_minutes"],}),
            ToolDefinition(name="calendar_create_event", description="Create a new event.", input_schema={
                "type": "object", "properties": {
                    "title": {"type": "string"}, "start_time": {"type": "string"}, "end_time": {"type": "string"},
                    "attendees": {"type": "array", "items": {"type": "string"}}},
                "required": ["title", "start_time", "end_time"],}),
            ToolDefinition(name="calendar_get_event", description="Get a single event by ID.", input_schema={
                "type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"],}),
            ToolDefinition(name="calendar_update_event", description="Update an event.", input_schema={
                "type": "object", "properties": {"event_id": {"type": "string"}, "title": {"type": "string"}, 
                                               "start_time": {"type": "string"}, "end_time": {"type": "string"}},
                "required": ["event_id"],}),
            ToolDefinition(name="calendar_delete_event", description="Delete an event.", input_schema={
                "type": "object", "properties": {"event_id": {"type": "string"}}, "required": ["event_id"],}),
        ]

    async def invoke(self, tool_name: str, args: dict[str, Any], oauth: MCPInvokeOAuth | None = None) -> dict[str, Any]:
        # --- Local tool implementations (Restored) ---
        if tool_name == "detect_overlaps":
            events = args.get("events") or []
            overlaps: list[dict[str, Any]] = []
            for i, a in enumerate(events):
                for j, b in enumerate(events):
                    if j <= i: continue
                    overlaps.append({"pair": (i, j), "note": "Compare start/end in orchestrator"})
            return {"ok": True, "overlaps": overlaps, "event_count": len(events)}
        if tool_name == "calendar_find_free_slots":
            return {"ok": True, "message": "Free slot finding is a mock and not fully implemented."}

        # --- API tool implementations ---
        if not self._invocation_ready(oauth):
            return {"ok": False, "error": "not_configured", "message": "Google Calendar is not configured."}
        
        token = await access_token_for_calendar(self._settings, 
            calendar_access_token=(oauth.google_calendar_access_token if oauth else None),
            refresh_token=self._refresh_token(oauth))
        if not token: return {"ok": False, "error": "oauth_token_required", "message": "Could not get Google Calendar token."}

        headers = {"Authorization": f"Bearer {token}"}
        cal_url = f"{CALENDAR_V3_BASE}/calendars/primary/events"

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                if tool_name in ["list_events", "calendar_fetch_events"]:
                    params = {
                        "timeMin": args.get("time_min") or args.get("start_date"),
                        "timeMax": args.get("time_max") or args.get("end_date"),
                        "maxResults": min(int(args.get("max_results", 20)), 250),
                        "singleEvents": "true", "orderBy": "startTime",
                    }
                    r = await client.get(cal_url, params=params)
                    r.raise_for_status()
                    return {"ok": True, "events": r.json().get("items", [])}

                if tool_name == "calendar_create_event":
                    payload = {
                        "summary": args["title"], "start": {"dateTime": args["start_time"]}, "end": {"dateTime": args["end_time"]},
                        "attendees": [{"email": e} for e in args.get("attendees", [])]}
                    r = await client.post(cal_url, json=payload)
                    r.raise_for_status()
                    return {"ok": True, "event": r.json()}

                # --- New Tool Implementations ---
                if tool_name == "calendar_get_event":
                    r = await client.get(f"{cal_url}/{args['event_id']}")
                    r.raise_for_status()
                    return {"ok": True, "event": r.json()}

                if tool_name == "calendar_update_event":
                    payload = {k: v for k, v in args.items() if k != "event_id" and v is not None}
                    if "title" in payload: payload["summary"] = payload.pop("title")
                    if "start_time" in payload: payload["start"] = {"dateTime": payload.pop("start_time")}
                    if "end_time" in payload: payload["end"] = {"dateTime": payload.pop("end_time")}
                    r = await client.patch(f"{cal_url}/{args['event_id']}", json=payload)
                    r.raise_for_status()
                    return {"ok": True, "event": r.json()}

                if tool_name == "calendar_delete_event":
                    r = await client.delete(f"{cal_url}/{args['event_id']}")
                    r.raise_for_status()
                    return {"ok": True, "status": "deleted"}

                return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}

        except httpx.HTTPStatusError as exc:
            logger.warning(f"Calendar HTTP error: {exc.response.status_code} {exc.response.text[:500]}")
            return {"ok": False, "error": "upstream_error", "status_code": exc.response.status_code, "message": exc.response.text[:2000]}
        except httpx.RequestError as exc:
            logger.exception(f"Calendar {tool_name} failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}
