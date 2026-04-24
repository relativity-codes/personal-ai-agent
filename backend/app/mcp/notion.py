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
    """Return a hyphenated UUID string accepted by the Notion API."""
    s = (raw or "").strip()
    if not s:
        raise ValueError("Notion ID is empty.")
    
    # Remove quotes if present
    while len(s) >= 2 and s[0] == s[-1] == '"':
        s = s[1:-1].strip()
    
    # Try parsing as a direct UUID first
    try:
        # uuid.UUID handles both hyphenated and non-hyphenated 32-char hex
        return str(uuid.UUID(s))
    except ValueError:
        pass
        
    # Search for any 32-character hex sequence in the string (handles URLs, etc.)
    m = re.search(r"([a-f0-9]{32})", s, re.I)
    if m:
        return str(uuid.UUID(m.group(1).lower()))
        
    raise ValueError(f"Could not parse a valid 32-character Notion ID from: {raw}")


def _notion_error_hint(
    response: httpx.Response,
    *,
    tool_name: str,
    parent_type: str | None,
) -> str | None:
    try:
        body = response.json()
    except Exception:
        return None
    msg = str(body.get("message") or "")
    code = str(body.get("code") or "")
    if tool_name == "create_page" and response.status_code == 404:
        if "object_not_found" in code or "could not find" in msg.lower():
            return (
                "In Notion: open the parent page or database → ⋮ or ⋯ → Connections → add this integration. "
                "If you used parent_type \"page_id\", confirm the ID is a page; use \"database_id\" for database parents."
            )
    if response.status_code == 400 and "page, not a database" in msg.lower():
        if parent_type == "database_id":
            return (
                "The ID is a page, not a database. Retry with parent_type \"page_id\" or use the database's ID as parent_id."
            )
    return None


def _notion_upstream_error(
    response: httpx.Response,
    *,
    tool_name: str,
    parent_type: str | None = None,
) -> dict[str, Any]:
    logger.warning("Notion HTTP error on %s: %s %s", tool_name, response.status_code, response.text[:500])
    out: dict[str, Any] = {
        "ok": False,
        "error": "upstream_error",
        "status_code": response.status_code,
        "message": response.text[:2000],
    }
    hint = _notion_error_hint(response, tool_name=tool_name, parent_type=parent_type)
    if hint:
        out["hint"] = hint
    return out


class NotionMCPServer(MCPServer):
    id = "notion"
    display_name = "Notion"
    description = "A comprehensive suite of tools for interacting with Notion pages and databases."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._token = (settings.NOTION_TOKEN or "").strip()

    def _effective_token(self, oauth: MCPInvokeOAuth | None) -> str:
        if oauth and oauth.notion_token:
            return oauth.notion_token.strip()
        return self._token

    def is_configured(self) -> bool:
        return bool(self._token)

    async def list_tools(self) -> list[ToolDefinition]:
        # Combining all existing and new tools
        tools = [
            # --- Original Tools ---
            ToolDefinition(name="query_database", description="Query a Notion database.", input_schema={
                "type": "object", "properties": {"database_id": {"type": "string"}, "page_size": {"type": "integer", "default": 10}},
                "required": ["database_id"],}),
            ToolDefinition(name="create_page", description="Create a page or database row.", input_schema={
                "type": "object", "properties": {
                    "parent_id": {"type": "string"}, "title": {"type": "string"},
                    "parent_type": {"type": "string", "enum": ["page_id", "database_id"], "default": "page_id"}},
                "required": ["parent_id", "title"],}),
            # --- Previously Added Tools ---
            ToolDefinition(name="notion_query_pages", description="Search pages in a database.", input_schema={
                "type": "object", "properties": {"database_id": {"type": "string"}, "query": {"type": "string"}, "filter": {"type": "object"}},
                "required": ["database_id"],}),
            ToolDefinition(name="notion_create_page", description="Create a new page with content.", input_schema={
                "type": "object", "properties": {"parent_id": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "array"}},
                "required": ["parent_id", "title"],}),
            ToolDefinition(name="notion_update_page", description="Update a page's title or content.", input_schema={
                "type": "object", "properties": {"page_id": {"type": "string"}, "title": {"type": "string"}, "content": {"type": "array"}},
                "required": ["page_id"],}),
            ToolDefinition(name="notion_get_agenda", description="Extract blocks from a page.", input_schema={
                "type": "object", "properties": {"page_id": {"type": "string"}}, "required": ["page_id"],}),
            # --- Newly Added Tools ---
            ToolDefinition(name="notion_get_page", description="Get a single Notion page's content.", input_schema={
                "type": "object", "properties": {"page_id": {"type": "string"}}, "required": ["page_id"],}),
            ToolDefinition(name="notion_get_database_schema", description="Get a database's structure.", input_schema={
                "type": "object", "properties": {"database_id": {"type": "string"}}, "required": ["database_id"],}),
            ToolDefinition(name="notion_add_comment", description="Add a comment to a page.", input_schema={
                "type": "object", "properties": {"page_id": {"type": "string"}, "comment": {"type": "string"}},
                "required": ["page_id", "comment"],}),
        ]
        return tools

    async def invoke(self, tool_name: str, args: dict[str, Any], oauth: MCPInvokeOAuth | None = None) -> dict[str, Any]:
        token = self._effective_token(oauth)
        if not token:
            return {"ok": False, "error": "not_configured", "message": "Notion token is not set."}

        headers = {"Authorization": f"Bearer {token}", "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"}
        base = "https://api.notion.com/v1"

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                # --- Route to the correct tool logic ---
                if tool_name == "query_database":
                    db_id = normalize_notion_resource_id(args["database_id"])
                    r = await client.post(f"{base}/databases/{db_id}/query", json={"page_size": min(int(args.get("page_size", 10)), 100)})
                elif tool_name == "create_page":
                    parent_id = normalize_notion_resource_id(args["parent_id"])
                    parent_key = "database_id" if args.get("parent_type") == "database_id" else "page_id"
                    payload = {"parent": {parent_key: parent_id}, "properties": {"title": {"title": [{"text": {"content": args["title"]}}]}}}
                    r = await client.post(f"{base}/pages", json=payload)
                elif tool_name in ["notion_query_pages", "gmail_search"]:
                    db_id = normalize_notion_resource_id(args["database_id"])
                    payload = {k: v for k, v in {"filter": args.get("filter"), "query": args.get("query")}.items() if v}
                    r = await client.post(f"{base}/databases/{db_id}/query", json=payload)
                elif tool_name == "notion_create_page":
                    parent_id = normalize_notion_resource_id(args["parent_id"])
                    payload = {"parent": {"page_id": parent_id}, "properties": {"title": {"title": [{"text": {"content": args["title"]}}]}}, "children": args.get("content", [])}
                    r = await client.post(f"{base}/pages", json=payload)
                    if not r.is_success and "is a database, not a page" in r.text:
                        payload["parent"] = {"database_id": parent_id}
                        r = await client.post(f"{base}/pages", json=payload)
                elif tool_name == "notion_update_page":
                    page_id = normalize_notion_resource_id(args["page_id"])
                    payload = {}
                    if "title" in args: payload["properties"] = {"title": {"title": [{"text": {"content": args["title"]}}]}}
                    if args.get("content"): await client.patch(f"{base}/blocks/{page_id}/children", json={"children": args["content"]}).raise_for_status()
                    r = await client.patch(f"{base}/pages/{page_id}", json=payload)
                elif tool_name == "notion_get_agenda":
                    page_id = normalize_notion_resource_id(args["page_id"])
                    r = await client.get(f"{base}/blocks/{page_id}/children")
                elif tool_name == "notion_get_page":
                    page_id = normalize_notion_resource_id(args["page_id"])
                    page_props = await client.get(f"{base}/pages/{page_id}")
                    page_props.raise_for_status()
                    page_blocks = await client.get(f"{base}/blocks/{page_id}/children")
                    page_blocks.raise_for_status()
                    return {"ok": True, "data": {"page": page_props.json(), "blocks": page_blocks.json()}}
                elif tool_name == "notion_get_database_schema":
                    db_id = normalize_notion_resource_id(args["database_id"])
                    r = await client.get(f"{base}/databases/{db_id}")
                elif tool_name == "notion_add_comment":
                    page_id = normalize_notion_resource_id(args["page_id"])
                    payload = {"parent": {"page_id": page_id}, "rich_text": [{"text": {"content": args["comment"]}}]}
                    r = await client.post(f"{base}/comments", json=payload)
                else:
                    return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}
                
                r.raise_for_status()
                return {"ok": True, "data": r.json()}

        except httpx.HTTPStatusError as exc:
            parent_type = args.get("parent_type") if tool_name == "create_page" else None
            return _notion_upstream_error(
                exc.response, tool_name=tool_name, parent_type=parent_type
            )
        except (httpx.RequestError, ValueError) as exc:
            logger.exception(f"Notion {tool_name} failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}
