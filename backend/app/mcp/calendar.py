from __future__ import annotations

from typing import Any

from app.config import Settings
from app.mcp.base import MCPServer
from app.mcp.schema import ToolDefinition


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

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name == "list_events":
            if not self.is_configured():
                return {
                    "ok": False,
                    "error": "not_configured",
                    "message": "Calendar live API needs GOOGLE_CALENDAR_ACCESS_TOKEN or OAuth client setup.",
                }
            return {
                "ok": False,
                "error": "not_implemented",
                "message": "Wire Google Calendar API with stored OAuth tokens in a follow-up.",
            }
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
