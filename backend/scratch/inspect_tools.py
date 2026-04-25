import asyncio
from app.mcp_alt.registry import mcp_alt_registry
import json

async def main():
    await mcp_alt_registry.initialize()
    server = mcp_alt_registry.get_server("github")
    if not server:
        print("Server not found")
        return
    tools = await server.list_tools()
    print(f"Found {len(tools)} tools")
    if tools:
        t = tools[0]
        print(f"Tool attributes: {dir(t)}")
        # Inspect the Tool object
        from mcp.types import Tool
        print(f"Is instance of mcp.types.Tool: {is_instance(t, Tool) if 'is_instance' in globals() else 'unknown'}")
        
        # In modern MCP, Tool has 'inputSchema' (camelCase)
        if hasattr(t, 'inputSchema'):
             print(f"inputSchema: {t.inputSchema}")
        elif hasattr(t, 'input_schema'):
             print(f"input_schema: {t.input_schema}")

if __name__ == "__main__":
    asyncio.run(main())
