from __future__ import annotations
import logging
from typing import Annotated, Any
from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_current_user
from app.db.database import get_db
from app.mcp.schema import InvokeRequest, InvokeResponse
# from app.mcp.registry import mcp_registry
from app.mcp_alt.registry import mcp_alt_registry
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

router = APIRouter()

_INVOKE_OPENAPI_EXAMPLES: dict[str, dict[str, Any]] = {
    "MY_GITHUB_list_prs": {
        "summary": "GitHub: list open PRs",
        "description": "Requires MY_GITHUB_TOKEN. Replace owner/repo.",
        "value": {
            "server_id": "github",
            "tool": "MY_GITHUB_list_prs",
            "arguments": {"owner": "octocat", "repo": "Hello-World", "state": "open"},
        },
    },
    "MY_GITHUB_list_commits": {
        "summary": "GitHub: list commits",
        "value": {
            "server_id": "github",
            "tool": "MY_GITHUB_list_commits",
            "arguments": {"owner": "octocat", "repo": "Hello-World", "branch": "main"},
        },
    },
    "notion_query_database": {
        "summary": "Notion: query database",
        "description": "Requires NOTION_TOKEN and a database shared with the integration.",
        "value": {
            "server_id": "notion",
            "tool": "query_database",
            "arguments": {"database_id": "YOUR_DATABASE_UUID", "page_size": 10},
        },
    },
    "notion_create_page": {
        "summary": "Notion: create page",
        "description": "parent_id = existing parent page/database (not the new child). Default parent_type page_id. Share the parent with your integration (⋯ → Connections).",
        "value": {
            "server_id": "notion",
            "tool": "create_page",
            "arguments": {
                "parent_id": "YOUR_PARENT_UUID",
                "title": "Standup agenda",
                "parent_type": "page_id",
            },
        },
    },
    "calendar_list_events": {
        "summary": "Calendar: list events",
        "description": "Uses user-scoped Google OAuth credentials (stored per user in DB). RFC3339 times.",
        "value": {
            "server_id": "calendar",
            "tool": "list_events",
            "arguments": {
                "time_min": "2026-04-22T00:00:00Z",
                "time_max": "2026-04-29T23:59:59Z",
                "max_results": 20,
            },
        },
    },
    "calendar_detect_overlaps": {
        "summary": "Calendar: detect overlaps (no Google token)",
        "value": {
            "server_id": "calendar",
            "tool": "detect_overlaps",
            "arguments": {
                "events": [
                    {"summary": "A", "start": "2026-04-22T14:00:00Z", "end": "2026-04-22T15:00:00Z"},
                    {"summary": "B", "start": "2026-04-22T14:30:00Z", "end": "2026-04-22T15:30:00Z"},
                ]
            },
        },
    },
    "gmail_list_threads": {
        "summary": "Gmail: list threads",
        "description": "Uses user-scoped Google OAuth credentials (with Gmail scope, stored per user in DB).",
        "value": {
            "server_id": "gmail",
            "tool": "list_threads",
            "arguments": {"query": "is:unread", "max_results": 10},
        },
    },
}


@router.get("/servers")
async def list_mcp_servers(
    db: AsyncSession = Depends(get_db),
    user: dict = Depends(get_current_user)
) -> dict[str, Any]:
    logger.debug("mcp.list_servers user_id=%s", user.get("user_id"))
    user_id = user.get("user_id")
    return {"servers": await mcp_alt_registry.list_servers(db, user_id)}


@router.get("/tools")
async def list_mcp_tools(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    logger.debug("mcp.list_tools user_id=%s", user.get("user_id"))
    integrations = await mcp_alt_registry.list_all_tools()
    return {"integrations": integrations}


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_mcp_tool(
    body: Annotated[
        InvokeRequest,
        Body(openapi_examples=_INVOKE_OPENAPI_EXAMPLES),
    ],
    user: dict = Depends(get_current_user),
) -> InvokeResponse:
    logger.info(
        "mcp.invoke",
        extra={
            "server_id": body.server_id,
            "tool": body.tool,
            "user_id": user.get("user_id"),
        },
    )
    try:
        user_id = user.get("user_id")
        raw = await mcp_alt_registry.invoke_tool(
            body.server_id, 
            body.tool, 
            body.arguments, 
            user_id=user_id
        )
    except Exception as exc:
        log_exception(
            logger, 
            exc, 
            context=f"MCP invocation crashed: server_id={body.server_id} tool={body.tool}",
            extra_data={"user_id": user.get("user_id"), "arguments": body.arguments}
        )
        raise HTTPException(
            status_code=500,
            detail=f"Tool invocation failed: {str(exc)}",
        ) from exc
    
    # Handle the result format from the new mcp-python-sdk
    # The result is often a CallToolResult object or a dict
    result_data = raw
    if hasattr(raw, 'content'):
        # If it's a CallToolResult, extract the content
        result_data = [
            {"type": c.type, "text": c.text} if hasattr(c, 'text') else str(c)
            for c in raw.content
        ]
    
    ok = True
    if isinstance(raw, dict) and "ok" in raw:
        ok = bool(raw["ok"])
    
    return InvokeResponse(
        ok=ok,
        server_id=body.server_id,
        tool=body.tool,
        result=result_data,
        error=None,
    )
