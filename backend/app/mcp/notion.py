from __future__ import annotations

import logging
import re
import uuid
from typing import Any

import httpx

from app.config import Settings
from app.mcp.base import MCPServer
from app.mcp.schema import MCPInvokeOAuth, ToolDefinition

logger = logging.getLogger(__name__)

NOTION_VERSION = "2022-06-28"

_RE_TAIL_32 = re.compile(r"([a-f0-9]{32})(?:\?[^#]*)?(?:#.*)?$", re.I)


def normalize_notion_resource_id(raw: str) -> str:
    """Return a hyphenated UUID string accepted by the Notion API.

    Accepts: full Notion page/database URLs, ``Title-`` + 32 hex (from Copy link),
    bare 32 hex, or a standard UUID string.
    """
    s = (raw or "").strip()
    while len(s) >= 2 and s[0] == s[-1] and s[0] in "\"'":
        s = s[1:-1].strip()
    s = s.replace("\\", "").strip()
    s_no_frag = s.split("?")[0].split("#")[0].rstrip("/")

    try:
        return str(uuid.UUID(s_no_frag))
    except ValueError:
        pass

    m = _RE_TAIL_32.search(s_no_frag)
    if not m:
        raise ValueError(
            "Notion IDs must be a UUID or 32-character hex id (optionally after a title slug, "
            "e.g. My-Page-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx) or a notion.so URL."
        )
    token = m.group(1).lower()
    return str(uuid.UUID(token))


def _notion_upstream_error(
    response: httpx.Response,
    *,
    tool_name: str,
    parent_type: str | None = None,
) -> dict[str, Any]:
    """Map a failed Notion HTTP response into our invoke result shape."""
    text = response.text[:2000]
    out: dict[str, Any] = {
        "ok": False,
        "error": "upstream_error",
        "status_code": response.status_code,
        "message": text,
    }
    try:
        data = response.json()
    except ValueError:
        return out
    code = data.get("code")
    api_msg = data.get("message") or ""
    msg = api_msg.lower()
    hints: list[str] = []

    if response.status_code == 400 and code == "validation_error":
        if "is a page, not a database" in msg and tool_name == "create_page":
            hints.append(
                "Use parent_type \"page_id\" (default) for a normal page parent. "
                "parent_type \"database_id\" is only for full-page or inline databases (tables)."
            )
        if "is a page, not a database" in msg and tool_name == "query_database":
            hints.append(
                "query_database only works on database objects. Use create_page with parent_type "
                "\"page_id\" if you need to work with a normal page."
            )

    if response.status_code == 404 and code == "object_not_found":
        if tool_name == "create_page":
            if parent_type == "page_id":
                hints.append(
                    "For parent_type \"page_id\", a 404 usually means the integration cannot see that page: "
                    "open the parent page in Notion → ⋯ → Connections → add this integration."
                )
                hints.append(
                    "Use parent_type \"database_id\" only when the parent is a database (table), not a normal page."
                )
            elif parent_type == "database_id":
                hints.append(
                    "If the parent is a normal page (including where you clicked “Add page”), use parent_type \"page_id\"."
                )
        if tool_name == "query_database":
            hints.append("Confirm the database id is correct and the database is shared with your integration.")
        if "share" in msg or "integration" in msg or "connections" in msg:
            hints.append(
                "In Notion: open the page or database → ⋮ or ⋯ → Connections → add your integration."
            )
    if hints:
        out["hint"] = " ".join(hints)
    return out


class NotionMCPServer(MCPServer):
    id = "notion"
    display_name = "Notion"
    description = "Query databases and create pages for agendas, tasks, and reports."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token = (settings.NOTION_TOKEN or "").strip()

    def is_configured(self) -> bool:
        return bool(self._token)

    def _effective_token(self, oauth: MCPInvokeOAuth | None) -> str:
        if oauth and (oauth.notion_token or "").strip():
            return oauth.notion_token.strip()
        return self._token

    async def list_tools(self) -> list[ToolDefinition]:
        return [
            ToolDefinition(
                name="query_database",
                description="Query a Notion database (returns pages matching filter/sorts).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "database_id": {
                            "type": "string",
                            "description": "Database UUID, 32-char hex, slug-hex from URL, or full notion.so database URL",
                        },
                        "page_size": {"type": "integer", "default": 10},
                    },
                    "required": ["database_id"],
                },
            ),
            ToolDefinition(
                name="create_page",
                description="Create a child page under a parent page (parent_type page_id) or a new row in a database (parent_type database_id).",
                input_schema={
                    "type": "object",
                    "properties": {
                        "parent_id": {
                            "type": "string",
                            "description": "The **existing** parent to attach under: the page you are on before “Add page” (not the new blank page’s URL). UUID, slug-hex from Copy link, or notion.so URL. Use parent_type database_id only for database (table) parents.",
                        },
                        "title": {"type": "string"},
                        "parent_type": {"type": "string", "enum": ["page_id", "database_id"], "default": "page_id"},
                    },
                    "required": ["parent_id", "title"],
                },
            ),
        ]

    async def invoke(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        oauth: MCPInvokeOAuth | None = None,
    ) -> dict[str, Any]:
        token = self._effective_token(oauth)
        if not token:
            return {
                "ok": False,
                "error": "not_configured",
                "message": "Set NOTION_TOKEN or pass oauth.notion_token on invoke.",
            }
        headers = {
            "Authorization": f"Bearer {token}",
            "Notion-Version": NOTION_VERSION,
            "Content-Type": "application/json",
        }
        base = "https://api.notion.com/v1"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                if tool_name == "query_database":
                    db_raw = arguments.get("database_id", "").strip()
                    if not db_raw:
                        return {"ok": False, "error": "validation_error", "message": "database_id is required."}
                    try:
                        db_id = normalize_notion_resource_id(db_raw)
                    except ValueError as exc:
                        return {"ok": False, "error": "validation_error", "message": str(exc)}
                    body: dict[str, Any] = {"page_size": min(int(arguments.get("page_size", 10)), 100)}
                    r = await client.post(f"{base}/databases/{db_id}/query", headers=headers, json=body)
                    r.raise_for_status()
                    return {"ok": True, "data": r.json()}
                if tool_name == "create_page":
                    parent_raw = arguments.get("parent_id", "").strip()
                    title = arguments.get("title", "")
                    parent_type = arguments.get("parent_type", "page_id")
                    if not parent_raw or not title:
                        return {"ok": False, "error": "validation_error", "message": "parent_id and title are required."}
                    try:
                        parent_id = normalize_notion_resource_id(parent_raw)
                    except ValueError as exc:
                        return {"ok": False, "error": "validation_error", "message": str(exc)}
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
                    if r.is_success:
                        return {"ok": True, "page": r.json()}
                    logger.warning(
                        "notion create_page failed: %s %s", r.status_code, r.text[:500]
                    )
                    return _notion_upstream_error(
                        r, tool_name="create_page", parent_type=parent_type
                    )
                return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
        except httpx.HTTPStatusError as exc:
            logger.warning("notion http error: %s %s", exc.response.status_code, exc.response.text[:500])
            parent_type_arg: str | None = None
            if tool_name == "create_page":
                parent_type_arg = str(arguments.get("parent_type", "page_id"))
            return _notion_upstream_error(
                exc.response, tool_name=tool_name, parent_type=parent_type_arg
            )
        except httpx.RequestError as exc:
            logger.exception("notion request failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}
