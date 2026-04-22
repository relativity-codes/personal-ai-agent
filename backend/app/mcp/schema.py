from typing import Any

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    name: str
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)


class InvokeRequest(BaseModel):
    server_id: str = Field(..., description="github | notion | calendar | gmail")
    tool: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class InvokeResponse(BaseModel):
    ok: bool
    server_id: str
    tool: str
    result: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
