import logging
from typing import Any, Dict, List, Optional
from mcp.server import Server

# Import our servers
from app.mcp_alt.github import server as github_server
from app.mcp_alt.notion import server as notion_server
from app.mcp_alt.calendar import server as calendar_server
from app.mcp_alt.gmail import server as gmail_server

logger = logging.getLogger(__name__)

class MCPAltRegistry:
    def __init__(self) -> None:
        self._servers: Dict[str, Server] = {
            "github": github_server,
            "notion": notion_server,
            "calendar": calendar_server,
            "gmail": gmail_server,
        }

    def get_server(self, server_id: str) -> Optional[Server]:
        return self._servers.get(server_id)

    def list_servers(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": server_id,
                "name": server_id.capitalize(),
                "tools_count": len(server.list_tools()) if hasattr(server, 'list_tools') else 0
            }
            for server_id, server in self._servers.items()
        ]

    async def list_all_tools(self) -> List[Dict[str, Any]]:
        out = []
        for server_id, server in self._servers.items():
            # In the mcp-python-sdk, Server.list_tools() is a sync or async method depending on version
            # Usually it returns a list of Tool objects
            try:
                tools = server.list_tools()
                out.append({
                    "server_id": server_id,
                    "tools": [
                        {
                            "name": t.name,
                            "description": t.description,
                            "input_schema": t.input_schema
                        } for t in tools
                    ]
                })
            except Exception as e:
                logger.error(f"Failed to list tools for {server_id}: {e}")
        return out

    async def initialize(self) -> None:
        logger.info("MCPAltRegistry initialized with %d servers", len(self._servers))

    def summary(self) -> Dict[str, Any]:
        return {
            "servers_count": len(self._servers),
            "servers": [
                {
                    "id": s_id,
                    "tools_count": len(server.list_tools())
                }
                for s_id, server in self._servers.items()
            ]
        }

    async def invoke_tool(self, server_id: str, tool_name: str, arguments: Dict[str, Any], user_id: Optional[str] = None) -> Any:
        server = self.get_server(server_id)
        if not server:
            raise ValueError(f"Unknown server: {server_id}")
        
        # Inject user_id if provided, so the tool can fetch credentials
        if user_id:
            arguments["user_id"] = user_id
            
        # Call the tool directly on the server instance
        return await server.call_tool(tool_name, arguments)

mcp_alt_registry = MCPAltRegistry()
