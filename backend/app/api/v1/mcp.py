from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_current_user
from app.mcp.schema import InvokeRequest, InvokeResponse
from app.services.mcp_registry import mcp_registry

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/servers")
async def list_mcp_servers(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    _ = user
    return {"servers": mcp_registry.list_servers()}


@router.get("/tools")
async def list_mcp_tools(user: dict = Depends(get_current_user)) -> dict[str, Any]:
    _ = user
    integrations = await mcp_registry.list_all_tools()
    return {"integrations": integrations}


@router.post("/invoke", response_model=InvokeResponse)
async def invoke_mcp_tool(
    body: InvokeRequest,
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
    raw = await server.invoke(body.tool, body.arguments)
    ok = bool(raw.get("ok")) if isinstance(raw, dict) else False
    err = raw.get("error") if isinstance(raw, dict) else None
    return InvokeResponse(
        ok=ok,
        server_id=body.server_id,
        tool=body.tool,
        result=raw if isinstance(raw, dict) else {"value": raw},
        error=str(err) if err else None,
    )
