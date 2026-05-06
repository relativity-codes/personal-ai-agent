from typing import Any, Dict, List, Optional
from langchain_core.tools import StructuredTool
from pydantic import create_model, BaseModel
from app.mcp_alt.registry import mcp_alt_registry
import logging

logger = logging.getLogger(__name__)

def create_mcp_tool(server_id: str, tool_name: str, description: str, input_schema: Dict[str, Any], user_id: str):
    """
    Creates a LangChain StructuredTool from an MCP tool definition.
    """
    
    # Extract properties for the pydantic model
    properties = input_schema.get("properties", {})
    required = input_schema.get("required", [])
    
    # Dynamically create a Pydantic model for the tool's input
    fields = {}
    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get("type", "string")
        # Map JSON schema types to Python types
        type_map = {
            "string": str,
            "number": float,
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict
        }
        py_type = type_map.get(prop_type, Any)
        
        # Determine if the field is required
        if prop_name in required:
            fields[prop_name] = (py_type, ...)
        else:
            fields[prop_name] = (Optional[py_type], None)

    # We don't want the user_id to be a parameter the LLM sees
    # It will be injected by the tool wrapper
    InputModel = create_model(f"{server_id}_{tool_name}_input", **fields)

    async def tool_func(**kwargs):
        # Filter out None values that LLM might have passed for optional fields
        # if the underlying tool doesn't support them
        clean_kwargs = {k: v for k, v in kwargs.items() if v is not None}
        
        logger.info(f"Invoking MCP tool: {server_id}/{tool_name} for user {user_id}")
        return await mcp_alt_registry.invoke_tool(
            server_id=server_id,
            tool_name=tool_name,
            arguments=clean_kwargs,
            user_id=str(user_id)
        )

    # Create the StructuredTool
    return StructuredTool(
        name=f"{server_id}_{tool_name}",
        description=description,
        args_schema=InputModel,
        coroutine=tool_func
    )

async def get_mcp_tools(user_id: str) -> List[StructuredTool]:
    """
    Fetches all available tools from the MCP registry and wraps them as LangChain tools.
    """
    # Ensure registry is initialized
    await mcp_alt_registry.initialize()
    
    all_tools_info = await mcp_alt_registry.list_all_tools()
    langchain_tools = []
    
    for server_info in all_tools_info:
        server_id = server_info["server_id"]
        for tool in server_info["tools"]:
            lc_tool = create_mcp_tool(
                server_id=server_id,
                tool_name=tool["name"],
                description=tool["description"],
                input_schema=tool["input_schema"],
                user_id=user_id
            )
            langchain_tools.append(lc_tool)
            
    return langchain_tools
