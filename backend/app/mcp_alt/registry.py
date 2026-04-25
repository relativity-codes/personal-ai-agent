import logging
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP as Server

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

    async def list_servers(self, db: Optional[Any] = None, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        from app.db.repositories.mcp_credential_repository import MCPCredentialRepository
        from app.api.deps import parse_uuid
        
        user_credentials = {}
        if db and user_id:
            try:
                uid = parse_uuid(user_id, "user_id")
                creds = await MCPCredentialRepository.get_by_user(db, uid)
                # Map server_id to True, and also handle the google -> calendar/gmail mapping
                user_credentials = {}
                for c in creds:
                    user_credentials[c.server_id] = True
                    if c.server_id == "google":
                        user_credentials["calendar"] = True
                        user_credentials["gmail"] = True
            except Exception as e:
                logger.error(f"Failed to fetch user credentials for registry: {e}")

        out = []
        for server_id, server in self._servers.items():
            tools_count = 0
            if hasattr(server, 'list_tools'):
                try:
                    tools = await server.list_tools()
                    tools_count = len(tools)
                except Exception:
                    pass
            
            out.append({
                "id": server_id,
                "name": server_id.capitalize(),
                "tools_count": tools_count,
                "configured": user_credentials.get(server_id, False)
            })
        return out

    async def list_all_tools(self) -> List[Dict[str, Any]]:
        out = []
        for server_id, server in self._servers.items():
            # In the mcp-python-sdk, Server.list_tools() is a sync or async method depending on version
            # Usually it returns a list of Tool objects
            try:
                tools = await server.list_tools()
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

    async def summary(self) -> Dict[str, Any]:
        servers_info = []
        for s_id, server in self._servers.items():
            tools = await server.list_tools()
            servers_info.append({
                "id": s_id,
                "tools_count": len(tools)
            })
            
        return {
            "servers_count": len(self._servers),
            "servers": servers_info
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
