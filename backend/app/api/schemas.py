from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime

class AuditLogRead(BaseModel):
    id: UUID
    session_id: str
    user_id: Optional[UUID]
    action: str
    input_text: Optional[str]
    intent_type: Optional[str]
    plan_id: Optional[UUID]
    success: Optional[bool]
    error_message: Optional[str]
    execution_time_ms: Optional[int]
    tokens_used: Optional[int]
    event_metadata: Optional[dict]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True

class ExecutionPlanRead(BaseModel):
    id: UUID
    user_id: UUID
    session_id: str
    intent_type: str
    status: Optional[str]
    task_status: Optional[dict]
    task_results: Optional[dict]
    task_errors: Optional[dict]
    execution_order: Optional[list]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatHistoryRead(BaseModel):
    id: UUID
    session_id: str
    role: str
    message: str
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True

class TaskRead(BaseModel):
    id: UUID
    session_id: str
    plan_id: UUID
    step: int
    description: str
    mcp_server: str
    tool: str
    parameters: dict
    depends_on: Optional[list]
    status: Optional[str]
    result: Optional[dict]
    error: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# SessionRead for session_router
class SessionRead(BaseModel):
    id: UUID
    user_id: UUID
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True
