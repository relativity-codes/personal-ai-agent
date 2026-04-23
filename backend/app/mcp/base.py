from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from app.mcp.schema import MCPInvokeOAuth, ToolDefinition


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
