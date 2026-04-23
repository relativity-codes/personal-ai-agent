from typing import TypedDict, List, Dict, Any, Optional, Annotated
from dataclasses import dataclass
from enum import Enum
import operator

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class Task(TypedDict):
    task_id: str
    step: int
    description: str
    mcp_server: str
    tool: str
    parameters: Dict[str, Any]
    depends_on: List[str]
    status: TaskStatus
    result: Optional[Any]
    error: Optional[str]

class AgentState(TypedDict):
    """State shared across all agents in the LangGraph workflow."""
    
    # User input
    user_id: str
    session_id: str
    user_input: str
    
    # Intent Agent output
    validated_intent: Optional[Dict[str, Any]]
    intent_confidence: float
    needs_clarification: bool
    clarification_question: Optional[str]
    
    # Task Planner state
    plan_id: Optional[str]
    tasks: Annotated[List[Task], operator.add]
    task_status: Dict[str, TaskStatus]
    execution_order: List[str]
    
    # Execution state
    current_task_index: int
    completed_tasks: Annotated[List[str], operator.add]
    failed_tasks: Annotated[List[Dict], operator.add]
    task_results: Annotated[Dict[str, Any], operator.setitem]
    
    # Final output
    final_response: Optional[str]
    error: Optional[str]
    
    # Metadata
    iteration: int
    max_iterations: int