from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from app.mcp.schema import MCPInvokeOAuth, ToolDefinition


class MCPUserBoundClient(Protocol):
    async def execute(self, tool: str, parameters: dict[str, Any]) -> dict[str, Any]: ...


class MCPRegistry(Protocol):
    def get_client(self, server_id: str, user_id: str) -> MCPUserBoundClient: ...


class MCPServer(ABC):
    id: str
    display_name: str
    description: str

    @abstractmethod
    def is_configured(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def list_tools(self) -> list[ToolDefinition]:
        raise NotImplementedError

    @abstractmethod
    async def invoke(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        oauth: MCPInvokeOAuth | None = None,
    ) -> dict[str, Any]:
        raise NotImplementedError
