from __future__ import annotations

from typing import Any

from app.config import Settings
from app.mcp.base import MCPServer
from app.mcp.schema import ToolDefinition


class GmailMCPServer(MCPServer):
    id = "gmail"
    display_name = "Gmail"
    description = "Optional v1.1: summarize threads and surface action items."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def is_configured(self) -> bool:
        return bool((self._settings.GMAIL_ACCESS_TOKEN or "").strip())

    async def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="list_threads",
                description="List recent threads (requires Gmail OAuth).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "default": "is:unread"},
                        "max_results": {"type": "integer", "default": 10},
                    },
                },
            ),
        ]

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if tool_name != "list_threads":
            return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
        if not self.is_configured():
            return {
                "ok": False,
                "error": "not_configured",
                "message": "Gmail is optional in v1; set GMAIL_ACCESS_TOKEN when OAuth is wired.",
            }
        return {
            "ok": False,
            "error": "not_implemented",
            "message": "Gmail API integration is deferred to v1.1.",
        }
