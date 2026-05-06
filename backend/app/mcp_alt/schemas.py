from typing import Any
from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)


class MCPInvokeOAuth(BaseModel):
    """Per-request credential overrides for MCP tools (until user vault is wired)."""

    github_token: str | None = None
    notion_token: str | None = None
    google_refresh_token: str | None = None
    google_calendar_access_token: str | None = None
    gmail_access_token: str | None = None


class InvokeRequest(BaseModel):
    server_id: str = Field(..., description="github | notion | calendar | gmail")
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)
    oauth: MCPInvokeOAuth | None = Field(
        default=None,
        description="Optional tokens for this invoke only (e.g. after /mcp/oauth/google/token).",
    )


class InvokeResponse(BaseModel):
    ok: bool
    server_id: str
    tool: str
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
