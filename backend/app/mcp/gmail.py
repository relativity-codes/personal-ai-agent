from __future__ import annotations

import base64
import logging
from typing import Any

import httpx

from app.config import Settings
from app.core.google_token import access_token_for_gmail
from app.mcp.base import MCPServer
from app.mcp.schema import MCPInvokeOAuth, ToolDefinition

logger = logging.getLogger(__name__)

GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1/users/me"


class GmailMCPServer(MCPServer):
    id = "gmail"
    display_name = "Gmail"
    description = "A comprehensive suite of tools for reading, searching, and composing emails."

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def _has_refresh_credentials(self, oauth: MCPInvokeOAuth | None) -> bool:
        return bool(
            self._settings.GOOGLE_CLIENT_ID
            and self._settings.GOOGLE_CLIENT_SECRET
            and oauth
            and (oauth.google_refresh_token or "").strip()
        )

    def _refresh_token(self, oauth: MCPInvokeOAuth | None) -> str:
        if oauth and (oauth.google_refresh_token or "").strip():
            return oauth.google_refresh_token.strip()
        return ""

    def _invocation_ready(self, oauth: MCPInvokeOAuth | None) -> bool:
        if oauth and (oauth.gmail_access_token or "").strip():
            return True
        return self._has_refresh_credentials(oauth)

    def is_configured(self) -> bool:
        return self._invocation_ready(None) or (self._settings.GOOGLE_CLIENT_ID and self._settings.GOOGLE_CLIENT_SECRET)

    async def list_tools(self) -> list[ToolDefinition]:
        # Preserving all existing tools and adding new ones
        return [
            ToolDefinition(name="list_threads", description="List recent email threads.", input_schema={
                "type": "object", "properties": {"query": {"type": "string", "default": "is:unread"}, "max_results": {"type": "integer", "default": 10}}}),
            ToolDefinition(name="gmail_search", description="Search for email threads.", input_schema={
                "type": "object", "properties": {"query": {"type": "string"}, "max_results": {"type": "integer", "default": 10}}, "required": ["query"]}),
            ToolDefinition(name="gmail_summarize_threads", description="Summarize recent threads.", input_schema={
                "type": "object", "properties": {"days_back": {"type": "integer", "default": 1}, "max_threads": {"type": "integer", "default": 5}}}),
            # --- New Tools ---
            ToolDefinition(name="gmail_get_thread", description="Get all messages in a thread.", input_schema={
                "type": "object", "properties": {"thread_id": {"type": "string"}}, "required": ["thread_id"]}),
            ToolDefinition(name="gmail_get_message", description="Get a single email message by ID.", input_schema={
                "type": "object", "properties": {"message_id": {"type": "string"}}, "required": ["message_id"]}),
            ToolDefinition(name="gmail_create_draft", description="Create a draft email. Requires gmail.compose scope.", input_schema={
                "type": "object", "properties": {
                    "to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject", "body"]}),
            ToolDefinition(name="gmail_send_email", description="Send an email. Requires gmail.send scope.", input_schema={
                "type": "object", "properties": {
                    "to": {"type": "string"}, "subject": {"type": "string"}, "body": {"type": "string"}},
                "required": ["to", "subject", "body"]}),
        ]

    async def invoke(self, tool_name: str, args: dict[str, Any], oauth: MCPInvokeOAuth | None = None) -> dict[str, Any]:
        if not self._invocation_ready(oauth):
            return {"ok": False, "error": "not_configured", "message": "Gmail is not configured."}

        token = await access_token_for_gmail(self._settings, 
            gmail_access_token=(oauth.gmail_access_token if oauth else None),
            refresh_token=self._refresh_token(oauth))
        if not token: return {"ok": False, "error": "oauth_token_required", "message": "Could not get Gmail access token."}

        headers = {"Authorization": f"Bearer {token}"}

        try:
            async with httpx.AsyncClient(timeout=30.0, headers=headers) as client:
                # --- Existing Tools (unchanged) ---
                if tool_name in ["list_threads", "gmail_search"]:
                    params = {"q": args.get("query", "is:unread"), "maxResults": min(int(args.get("max_results", 10)), 100)}
                    r = await client.get(f"{GMAIL_API_BASE}/threads", params=params)
                    r.raise_for_status()
                    return {"ok": True, "threads": r.json().get("threads", [])}
                
                elif tool_name == "gmail_summarize_threads":
                    params = {"q": f"newer_than:{args.get('days_back', 1)}d", "maxResults": min(int(args.get("max_threads", 5)), 100)}
                    r = await client.get(f"{GMAIL_API_BASE}/threads", params=params)
                    r.raise_for_status()
                    return {"ok": True, "threads": r.json().get("threads", [])}

                # --- New Tools ---
                elif tool_name == "gmail_get_thread":
                    r = await client.get(f"{GMAIL_API_BASE}/threads/{args['thread_id']}")
                    r.raise_for_status()
                    return {"ok": True, "thread": r.json()}

                elif tool_name == "gmail_get_message":
                    r = await client.get(f"{GMAIL_API_BASE}/messages/{args['message_id']}")
                    r.raise_for_status()
                    return {"ok": True, "message": r.json()}

                elif tool_name in ["gmail_create_draft", "gmail_send_email"]:
                    raw_email = (
                        f"From: me\r\n"
                        f"To: {args['to']}\r\n"
                        f"Subject: {args['subject']}\r\n\r\n"
                        f"{args['body']}"
                    ).encode("utf-8")
                    payload = {"raw": base64.urlsafe_b64encode(raw_email).decode("ascii")}
                    
                    endpoint = "drafts" if tool_name == "gmail_create_draft" else "messages/send"
                    r = await client.post(f"{GMAIL_API_BASE}/{endpoint}", json={'message': payload} if endpoint == 'drafts' else payload)
                    r.raise_for_status()
                    return {"ok": True, "result": r.json()}

                else:
                    return {"ok": False, "error": "unknown_tool", "message": f"Unknown tool: {tool_name}"}

        except httpx.HTTPStatusError as exc:
            logger.warning(f"Gmail HTTP error: {exc.response.status_code} {exc.response.text[:500]}")
            return {"ok": False, "error": "upstream_error", "status_code": exc.response.status_code, "message": exc.response.text[:2000]}
        except httpx.RequestError as exc:
            logger.exception(f"Gmail request failed")
            return {"ok": False, "error": "request_error", "message": str(exc)}
