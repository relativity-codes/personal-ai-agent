from __future__ import annotations

import logging
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException

from app.api.deps import get_current_user
from app.mcp.schema import InvokeRequest, InvokeResponse
from app.mcp.registry import mcp_registry

logger = logging.getLogger(__name__)

router = APIRouter()

_INVOKE_OPENAPI_EXAMPLES: dict[str, dict[str, Any]] = {
    "github_list_prs": {
        "summary": "GitHub: list open PRs",
        "description": "Requires GITHUB_TOKEN. Replace owner/repo.",
        "value": {
            "server_id": "github",
            "tool": "github_list_prs",
            "arguments": {"owner": "octocat", "repo": "Hello-World", "state": "open"},
        },
    },
    "github_list_commits": {
        "summary": "GitHub: list commits",
        "value": {
            "server_id": "github",
            "tool": "github_list_commits",
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
        "description": "Uses GOOGLE_REFRESH_TOKEN+client id/secret or GOOGLE_CALENDAR_ACCESS_TOKEN. RFC3339 times.",
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
        "description": "Uses GOOGLE_REFRESH_TOKEN+client id/secret (with Gmail scope) or GMAIL_ACCESS_TOKEN.",
        "value": {
            "server_id": "gmail",
            "tool": "list_threads",
            "arguments": {"query": "is:unread", "max_results": 10},
        },
    },
}


@router.get("/servers")
async def list_mcp_servers(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    logger.debug("mcp.list_servers user_id=%s", user.get("user_id"))
    return {"servers": mcp_registry.list_servers()}


@router.get("/tools")
async def list_mcp_tools(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    logger.debug("mcp.list_tools user_id=%s", user.get("user_id"))
    integrations = await mcp_registry.list_all_tools()
    return {"integrations": integrations}


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_mcp_tool(
    body: Annotated[
        InvokeRequest,
        Body(openapi_examples=_INVOKE_OPENAPI_EXAMPLES),
    ],
    user: dict = Depends(get_current_user),
) -> InvokeResponse:
    server = mcp_registry.get(body.server_id)
    if server is None:
        raise HTTPException(status_code=404, detail=f"Unknown server_id: {body.server_id}")
    tool_names = {t.name for t in await server.list_tools()}
    if body.tool not in tool_names:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown tool {body.tool!r} for server {body.server_id!r}",
        )
    logger.info(
        "mcp.invoke",
        extra={
            "server_id": body.server_id,
            "tool": body.tool,
            "user_id": user.get("user_id"),
        },
    )
    try:
        raw = await server.invoke(body.tool, body.arguments, body.oauth)
    except Exception as exc:
        logger.exception(
            "mcp.invoke crashed server_id=%s tool=%s",
            body.server_id,
            body.tool,
        )
        raise HTTPException(
            status_code=500,
            detail="Tool invocation failed; see server logs.",
        ) from exc
    ok = bool(raw.get("ok")) if isinstance(raw, dict) else False
    err = raw.get("error") if isinstance(raw, dict) else None
    return InvokeResponse(
        ok=ok,
        server_id=body.server_id,
        tool=body.tool,
        result=raw if isinstance(raw, dict) else {"value": raw},
        error=str(err) if err else None,
    )
