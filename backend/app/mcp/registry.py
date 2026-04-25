from __future__ import annotations

import logging
from typing import Any

from app.config import settings
from app.mcp.base import MCPServer
from app.mcp.calendar import CalendarMCPServer
from app.mcp.gmail import GmailMCPServer
from app.mcp.github import GitHubMCPServer
from app.mcp.notion import NotionMCPServer

logger = logging.getLogger(__name__)


class _UserBoundMCPClient:
    """LangGraph action node: ``execute`` → ``MCPServer.invoke`` (no per-user vault in this build)."""

    def __init__(self, service: MCPRegistryService, server_id: str, user_id: str) -> None:
        self._service = service
        self._server_id = server_id
        self._user_id = user_id

    async def execute(self, tool: str, parameters: dict[str, Any]) -> dict[str, Any]:
        _ = self._user_id
        server = self._service.get(self._server_id)
        if server is None:
            raise ValueError(f"Unknown MCP server_id: {self._server_id!r}")
        raw = await server.invoke(tool, parameters, None)
        return raw if isinstance(raw, dict) else {"value": raw}


class MCPRegistryService:
    def __init__(self) -> None:
        self._servers: dict[str, MCPServer] = {}

    async def initialize(self) -> None:
        self._servers = {
            GitHubMCPServer.id: GitHubMCPServer(settings),
            NotionMCPServer.id: NotionMCPServer(settings),
            CalendarMCPServer.id: CalendarMCPServer(settings),
            GmailMCPServer.id: GmailMCPServer(settings),
        }
        configured = sum(1 for s in self._servers.values() if s.is_configured())
        logger.info(
            "mcp registry ready servers=%s configured=%s/%s",
            list(self._servers.keys()),
            configured,
            len(self._servers),
        )

    def get(self, server_id: str) -> MCPServer | None:
        if server_id == "google_calendar":
            server_id = "calendar"
        return self._servers.get(server_id)

    def get_client(self, server_id: str, user_id: str) -> _UserBoundMCPClient:
        return _UserBoundMCPClient(self, server_id, user_id)

    def list_servers(self) -> list[dict[str, Any]]:
        return [
            {
                "id": s.id,
                "name": s.display_name,
                "description": s.description,
                "configured": s.is_configured(),
            }
            for s in self._servers.values()
        ]

    def summary(self) -> dict[str, Any]:
        total = len(self._servers)
        configured = sum(1 for s in self._servers.values() if s.is_configured())
        return {"total": total, "configured": configured}

    async def list_all_tools(self) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for s in self._servers.values():
            tools = await s.list_tools()
            out.append(
                {
                    "server_id": s.id,
                    "server_name": s.display_name,
                    "tools": [t.model_dump() for t in tools],
                }
            )
        return out


mcp_registry = MCPRegistryService()
