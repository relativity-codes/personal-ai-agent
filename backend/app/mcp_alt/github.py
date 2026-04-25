import os
import logging
from typing import Optional, Any, Dict, List
import httpx
from mcp.server.fastmcp import FastMCP

from app.mcp_alt.utils import get_mcp_credentials
from app.api.schemas import MCPServiceId

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-github")

server = FastMCP("github")

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
BASE_URL = "https://api.github.com"

async def get_headers(token: Optional[str] = None, user_id: Optional[str] = None) -> Dict[str, str]:
    
    if not user_id:
        logger.exception("Error refreshing Github token: No user ID provided")
        return None
    creds = await get_mcp_credentials(user_id, MCPServiceId.GITHUB)
    if not creds and not "token" in creds:
        logger.exception("Error refreshing Github token: No user ID provided")
        return None
    t = creds["token"]
            
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "credentials": "include",
        "Authorization": f"Bearer {t}"
    }
    return headers

async def handle_response(r: httpx.Response) -> Dict[str, Any]:
    try:
        r.raise_for_status()
        return {"ok": True, "data": r.json()}
    except httpx.HTTPStatusError as exc:
        logger.warning(f"GitHub HTTP error: {exc.response.status_code} {exc.response.text[:500]}")
        return {
            "ok": False, 
            "error": "upstream_error", 
            "status_code": exc.response.status_code, 
            "message": exc.response.text[:2000]
        }
    except Exception as e:
        logger.exception("GitHub request failed")
        return {"ok": False, "error": "request_error", "message": str(e)}

@server.tool()
async def github_list_prs(owner: str, repo: str, state: str = "open", user_id: Optional[str] = None) -> Dict[str, Any]:
    """List pull requests for a repository."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}/pulls", params={"state": state})
        return await handle_response(r)

@server.tool()
async def github_get_pr_details(owner: str, repo: str, pr_number: int, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get the details of a specific pull request."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}")
        return await handle_response(r)

@server.tool()
async def github_list_commits(owner: str, repo: str, branch: str = "main", user_id: Optional[str] = None) -> Dict[str, Any]:
    """List commits on a branch."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}/commits", params={"sha": branch})
        return await handle_response(r)

@server.tool()
async def github_create_issue(owner: str, repo: str, title: str, body: str = "", user_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new issue in a repository."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.post(f"{BASE_URL}/repos/{owner}/{repo}/issues", json={"title": title, "body": body})
        return await handle_response(r)

@server.tool()
async def github_summarize_pr(owner: str, repo: str, pr_number: int, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get the diff of a pull request for summarization."""
    headers = await get_headers(user_id=user_id)
    headers["Accept"] = "application/vnd.github.v3.diff"
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}")
        if r.is_success:
            return {"ok": True, "diff": r.text}
        return await handle_response(r)

@server.tool()
async def github_get_repo_details(owner: str, repo: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get high-level details about a repository."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}")
        return await handle_response(r)

@server.tool()
async def github_list_repo_contents(owner: str, repo: str, path: str = "", user_id: Optional[str] = None) -> Dict[str, Any]:
    """List files and directories at a given path in a repository."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.get(f"{BASE_URL}/repos/{owner}/{repo}/contents/{path}")
        return await handle_response(r)

@server.tool()
async def github_add_pr_comment(owner: str, repo: str, pr_number: int, comment: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Add a comment to an existing pull request."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.post(f"{BASE_URL}/repos/{owner}/{repo}/issues/{pr_number}/comments", json={"body": comment})
        return await handle_response(r)

@server.tool()
async def github_create_pr(owner: str, repo: str, head: str, base: str, title: str, body: str = "", user_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a new pull request."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        payload = {"head": head, "base": base, "title": title, "body": body}
        r = await client.post(f"{BASE_URL}/repos/{owner}/{repo}/pulls", json=payload)
        return await handle_response(r)

@server.tool()
async def github_merge_pr(owner: str, repo: str, pr_number: int, merge_method: str = "merge", user_id: Optional[str] = None) -> Dict[str, Any]:
    """Merge a pull request."""
    async with httpx.AsyncClient(timeout=30.0, headers=await get_headers(user_id=user_id)) as client:
        r = await client.put(f"{BASE_URL}/repos/{owner}/{repo}/pulls/{pr_number}/merge", json={"merge_method": merge_method})
        return await handle_response(r)

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())
