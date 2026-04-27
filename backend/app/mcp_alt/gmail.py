from app.mcp_alt.utils import save_mcp_credentials
from app.mcp_alt.utils import get_mcp_credentials
from app.api.schemas import MCPServiceId
import os
import base64
import logging
from typing import Optional, Any, Dict, List
import httpx
from mcp.server.fastmcp import FastMCP
import os
import time
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp-gmail")

server = FastMCP("gmail")

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"


async def get_token(user_id: Optional[str] = None, refresh: bool = False) -> Optional[str]:
    """
    Retrieve a valid Gmail access token using refresh token flow.
    Caches token until expiry to avoid unnecessary requests.
    """
    if not user_id:
        logger.exception("Error refreshing Gmail token: No user ID provided")
        return None
    creds = await get_mcp_credentials(user_id, MCPServiceId.GOOGLE)
    
    if creds.get("access_token") and not refresh:
        return creds["access_token"]    

    # 2. Load required credentials
    from app.config import settings
    refresh_token = creds.get("refresh_token")
    client_id = creds.get("client_id") or settings.GOOGLE_CLIENT_ID
    client_secret = creds.get("client_secret") or settings.GOOGLE_CLIENT_SECRET

    if not refresh_token or not client_id or not client_secret:
        logger.error("Missing Gmail OAuth credentials for user")
        return None

    # 3. Request new access token
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "refresh_token": refresh_token,
                    "grant_type": "refresh_token",
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )

        if response.status_code != 200:
            logger.error(f"Failed to refresh token: {response.text}")
            return None

        token_data = response.json()

        new_access_token = token_data.get("access_token")
        new_refresh_token = token_data.get("refresh_token")  # May be omitted unless rotated

        if not new_access_token:
            logger.error("No access_token in response")
            return None
        
        creds["access_token"] = new_access_token
        # Preserve existing refresh token when provider does not rotate/return it.
        if new_refresh_token:
            creds["refresh_token"] = new_refresh_token
        await save_mcp_credentials(user_id=user_id, server_id=MCPServiceId.GOOGLE, credentials=creds)
        return new_access_token
        
    except Exception as e:
        logger.exception("Error refreshing Gmail token")
        return None

async def get_headers(user_id: Optional[str] = None, refresh: bool = False) -> Dict[str, str]:
    try:
        token = await get_token(user_id, refresh=refresh)
        if token:
            return {"Authorization": f"Bearer {token}"}
        return {}
    except Exception as e:
        logger.exception("Error getting Gmail headers")
        return {}

@server.tool()
async def list_threads(query: str = "is:unread", max_results: int = 10, user_id: Optional[str] = None) -> Dict[str, Any]:
    """List recent email threads."""
    headers = await get_headers(user_id)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        params = {"q": query, "maxResults": min(max_results, 100)}
        r = await client.get(f"{GMAIL_API_BASE}/threads", params=params)
        
        if r.status_code == 401:
            # Retry with refreshed token
            logger.info("Gmail 401, refreshing token...")
            new_headers = await get_headers(user_id, refresh=True)
            async with httpx.AsyncClient(timeout=30.0, headers=new_headers) as client_retry:
                r = await client_retry.get(f"{GMAIL_API_BASE}/threads", params=params)
        
        r.raise_for_status()
        return {"ok": True, "threads": r.json().get("threads", [])}

@server.tool()
async def gmail_search(query: str, max_results: int = 10, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Search for email threads."""
    headers = await get_headers(user_id)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        params = {"q": query, "maxResults": min(max_results, 100)}
        r = await client.get(f"{GMAIL_API_BASE}/threads", params=params)
        
        if r.status_code == 401:
            logger.info("Gmail 401, refreshing token...")
            new_headers = await get_headers(user_id, refresh=True)
            async with httpx.AsyncClient(timeout=30.0, headers=new_headers) as client_retry:
                r = await client_retry.get(f"{GMAIL_API_BASE}/threads", params=params)

        r.raise_for_status()
        return {"ok": True, "threads": r.json().get("threads", [])}

@server.tool()
async def gmail_summarize_threads(days_back: int = 1, max_threads: int = 5, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Summarize recent threads."""
    headers = await get_headers(user_id)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        params = {"q": f"newer_than:{days_back}d", "maxResults": min(max_threads, 100)}
        r = await client.get(f"{GMAIL_API_BASE}/threads", params=params)
        
        if r.status_code == 401:
            logger.info("Gmail 401, refreshing token...")
            new_headers = await get_headers(user_id, refresh=True)
            async with httpx.AsyncClient(timeout=30.0, headers=new_headers) as client_retry:
                r = await client_retry.get(f"{GMAIL_API_BASE}/threads", params=params)

        r.raise_for_status()
        return {"ok": True, "threads": r.json().get("threads", [])}

@server.tool()
async def gmail_get_thread(thread_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get all messages in a thread."""
    headers = await get_headers(user_id)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        r = await client.get(f"{GMAIL_API_BASE}/threads/{thread_id}")
        
        if r.status_code == 401:
            logger.info("Gmail 401, refreshing token...")
            new_headers = await get_headers(user_id, refresh=True)
            async with httpx.AsyncClient(timeout=30.0, headers=new_headers) as client_retry:
                r = await client_retry.get(f"{GMAIL_API_BASE}/threads/{thread_id}")

        r.raise_for_status()
        return {"ok": True, "thread": r.json()}

@server.tool()
async def gmail_get_message(message_id: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Get a single email message by ID."""
    headers = await get_headers(user_id)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        r = await client.get(f"{GMAIL_API_BASE}/messages/{message_id}")
        
        if r.status_code == 401:
            logger.info("Gmail 401, refreshing token...")
            new_headers = await get_headers(user_id, refresh=True)
            async with httpx.AsyncClient(timeout=30.0, headers=new_headers) as client_retry:
                r = await client_retry.get(f"{GMAIL_API_BASE}/messages/{message_id}")

        r.raise_for_status()
        return {"ok": True, "message": r.json()}

@server.tool()
async def gmail_create_draft(to: str, subject: str, body: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a draft email."""
    headers = await get_headers(user_id)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        raw_email = (
            f"From: me\r\n"
            f"To: {to}\r\n"
            f"Subject: {subject}\r\n\r\n"
            f"{body}"
        ).encode("utf-8")
        payload = {"raw": base64.urlsafe_b64encode(raw_email).decode("ascii")}
        r = await client.post(f"{GMAIL_API_BASE}/drafts", json={'message': payload})
        
        if r.status_code == 401:
            logger.info("Gmail 401, refreshing token...")
            new_headers = await get_headers(user_id, refresh=True)
            async with httpx.AsyncClient(timeout=30.0, headers=new_headers) as client_retry:
                r = await client_retry.post(f"{GMAIL_API_BASE}/drafts", json={'message': payload})

        r.raise_for_status()
        return {"ok": True, "result": r.json()}

@server.tool()
async def gmail_send_email(to: str, subject: str, body: str, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Send an email."""
    headers = await get_headers(user_id)
    async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
        raw_email = (
            f"From: me\r\n"
            f"To: {to}\r\n"
            f"Subject: {subject}\r\n\r\n"
            f"{body}"
        ).encode("utf-8")
        payload = {"raw": base64.urlsafe_b64encode(raw_email).decode("ascii")}
        r = await client.post(f"{GMAIL_API_BASE}/messages/send", json=payload)
        
        if r.status_code == 401:
            logger.info("Gmail 401, refreshing token...")
            new_headers = await get_headers(user_id, refresh=True)
            async with httpx.AsyncClient(timeout=30.0, headers=new_headers) as client_retry:
                r = await client_retry.post(f"{GMAIL_API_BASE}/messages/send", json=payload)

        r.raise_for_status()
        return {"ok": True, "result": r.json()}

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio

    async def main():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())
    
    asyncio.run(main())
