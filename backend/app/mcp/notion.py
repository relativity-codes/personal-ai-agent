from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import Settings
from app.mcp.base import MCPServer
from app.mcp.schema import ToolDefinition

logger = logging.getLogger(__name__)

NOTION_VERSION = "2022-06-28"


class NotionMCPServer(MCPServer):
    id = "notion"
    display_name = "Notion"
    description = "Query databases and create pages for agendas, tasks, and reports."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token = (settings.NOTION_TOKEN or "").strip()

    def is_configured(self) -> bool:
        return bool(self._token)

    async def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="query_database",
                description="Query a Notion database (returns pages matching filter/sorts).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "database_id": {"type": "string", "description": "Notion database UUID"},
                        "page_size": {"type": "integer", "default": 10},
                    },
                    "required": ["database_id"],
                },
            ),
            ToolDefinition(
                name="create_page",
                description="Create a simple page under a parent page or database.",
                input_schema={
                    "type": "object",
                    "properties": {
                        "parent_id": {"type": "string", "description": "Parent page or database ID"},
                        "title": {"type": "string"},
                        "parent_type": {"type": "string", "enum": ["page_id", "database_id"], "default": "page_id"},
                    },
                    "required": ["parent_id", "title"],
                },
            ),
        ]

    async def invoke(self, tool_name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if not self.is_configured():
            return {
                "ok": False,
                "error": "not_configured",
                "message": "Set NOTION_TOKEN (integration token) in the environment.",
            }
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }
        base = "https://api.notion.com/v1"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if tool_name == "query_database":
                    db_id = arguments.get("database_id", "").strip()
                    if not db_id:
                        return {"ok": False, "error": "validation_error", "message": "database_id is required."}
                    body: dict[str, Any] = {"page_size": min(int(arguments.get("page_size", 10)), 100)}
                    r = await client.post(f"{base}/databases/{db_id}/query", headers=headers, json=body)
                    r.raise_for_status()
                    return {"ok": True, "data": r.json()}
                if tool_name == "create_page":
                    parent_id = arguments.get("parent_id", "").strip()
                    title = arguments.get("title", "")
                    parent_type = arguments.get("parent_type", "page_id")
                    if not parent_id or not title:
                        return {"ok": False, "error": "validation_error", "message": "parent_id and title are required."}
                    parent_key = "database_id" if parent_type == "database_id" else "page_id"
                    payload = {
                        "parent": {parent_key: parent_id},
                        "properties": {
                            "title": {
                                "title": [{"type": "text", "text": {"content": title}}],
                            }
                        },
                    }
                    r = await client.post(f"{base}/pages", headers=headers, json=payload)
                    r.raise_for_status()
                    return {"ok": True, "page": r.json()}
                return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
        except httpx.HTTPStatusError as exc:
            logger.warning("notion http error: %s %s", exc.response.status_code, exc.response.text[:500])
            return {
                "ok": False,
                "error": "upstream_error",
                "status_code": exc.response.status_code,
                "message": exc.response.text[:2000],
            }
        except httpx.RequestError as exc:
            logger.exception("notion request failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}
