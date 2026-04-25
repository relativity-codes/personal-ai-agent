import os
import re
import uuid
import logging
from typing import Optional, Any, List, Dict
from mcp.server.fastmcp import FastMCP
from notion_client import Client
from app.mcp_alt.utils import get_mcp_credentials
from app.api.schemas import MCPServiceId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-notion")

server = FastMCP("notion")

# Global client for env-based fallback
NOTION_TOKEN = os.environ.get("NOTION_API_KEY") or os.environ.get("NOTION_TOKEN")
default_notion = Client(auth=NOTION_TOKEN) if NOTION_TOKEN else None

async def get_client(user_id: Optional[str] = None) -> Optional[Client]:
    if user_id:
        creds = await get_mcp_credentials(user_id, MCPServiceId.NOTION)
        if creds and "token" in creds:
            return Client(auth=creds["token"])
    return default_notion

def normalize_notion_resource_id(raw: str) -> str:
    """Return a hyphenated UUID string accepted by the Notion API."""
    s = (raw or "").strip()
    if not s:
        raise ValueError("Notion ID is empty.")
    
    # Remove quotes if present
    while len(s) >= 2 and s[0] == s[-1] == '"':
        s = s[1:-1].strip()
    
    # Try parsing as a direct UUID first
    try:
        return str(uuid.UUID(s))
    except ValueError:
        pass
        
    # Search for any 32-character hex sequence in the string
    m = re.search(r"([a-f0-9]{32})", s, re.I)
    if m:
        return str(uuid.UUID(m.group(1).lower()))
        
    raise ValueError(f"Could not parse a valid 32-character Notion ID from: {raw}")

@server.tool()
async def query_database(database_id: str, page_size: int = 10, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Query a Notion database."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    db_id = normalize_notion_resource_id(database_id)
    return notion.databases.query(database_id=db_id, page_size=min(page_size, 100))

@server.tool()
async def create_page(
    parent_id: str, 
    title: str, 
    parent_type: str = "page_id",
    content: Optional[str] = None,
    user_id: Optional[str] = None
) -> Dict[str, Any]:
    """Create a page or database row."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    normalized_parent_id = normalize_notion_resource_id(parent_id)
    parent = {parent_type: normalized_parent_id}
    
    properties = {
        "title": [{"text": {"content": title}}]
    } if parent_type == "page_id" else {
        "Name": {"title": [{"text": {"content": title}}]}
    }

    children = []
    if content:
        children.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [{"type": "text", "text": {"content": content}}]
            }
        })

    return notion.pages.create(
        parent=parent,
        properties=properties,
        children=children if children else None
    )

@server.tool()
async def notion_query_pages(database_id: str, query: Optional[str] = None, filter: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Search pages in a database."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    db_id = normalize_notion_resource_id(database_id)
    return notion.databases.query(
        database_id=db_id,
        filter=filter,
    )

@server.tool()
async def notion_create_page(parent_id: str, title: str, content: Optional[List[Dict[str, Any]]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new page with content blocks."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    p_id = normalize_notion_resource_id(parent_id)
    try:
        return notion.pages.create(
            parent={"page_id": p_id},
            properties={"title": [{"text": {"content": title}}]},
            children=content
        )
    except Exception as e:
        if "is a database, not a page" in str(e):
            return notion.pages.create(
                parent={"database_id": p_id},
                properties={"title": {"title": [{"text": {"content": title}}]}},
                children=content
            )
        raise e

@server.tool()
async def notion_update_page(page_id: str, title: Optional[str] = None, content: Optional[List[Dict[str, Any]]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Update a page's title or content."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    p_id = normalize_notion_resource_id(page_id)
    if title:
        notion.pages.update(page_id=p_id, properties={"title": [{"text": {"content": title}}]})
    
    if content:
        notion.blocks.children.append(block_id=p_id, children=content)
    
    return {"ok": True, "message": "Page updated."}

@server.tool()
async def notion_get_agenda(page_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Extract blocks from a page."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    p_id = normalize_notion_resource_id(page_id)
    return notion.blocks.children.list(block_id=p_id)

@server.tool()
async def notion_get_page(page_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get a single Notion page's content and its blocks."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    p_id = normalize_notion_resource_id(page_id)
    page = notion.pages.retrieve(page_id=p_id)
    blocks = notion.blocks.children.list(block_id=p_id)
    return {"ok": True, "data": {"page": page, "blocks": blocks}}

@server.tool()
async def notion_get_database_schema(database_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get a database's structure."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    db_id = normalize_notion_resource_id(database_id)
    return notion.databases.retrieve(database_id=db_id)

@server.tool()
async def notion_add_comment(page_id: str, comment: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Add a comment to a page."""
    notion = await get_client(user_id)
    if not notion:
        return {"ok": False, "error": "not_configured", "message": "Notion API key not set."}
    
    p_id = normalize_notion_resource_id(page_id)
    return notion.comments.create(
        parent={"page_id": p_id},
        rich_text=[{"text": {"content": comment}}]
    )

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())
