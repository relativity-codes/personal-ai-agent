import asyncio
import time
from typing import Dict, Any, List
import logging
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

from app.agents.state import AgentState, TaskStatus
from app.mcp.base import MCPRegistry
from app.services.cache_service import redis_client
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository

class ActionAgent:
    """
    Action Agent: Executes MCP server calls.
    """
    
    def __init__(self, mcp_registry: MCPRegistry, user_repo: UserRepository, audit_repo: AuditRepository):
        self.mcp_registry = mcp_registry
        self.user_repo = user_repo
        self.audit_repo = audit_repo
    
    async def execute_task(self, state: AgentState, task: Dict) -> AgentState:
        """
        Execute a single task via MCP server.
        """
        task_id = task["task_id"]
        mcp_server = task["mcp_server"]
        tool = task["tool"]
        parameters = task["parameters"]
        
        start_time = time.time()
        
        try:
            # Get MCP client for user
            principal = state.get("google_id") or state["user_id"]
            mcp_client = self.mcp_registry.get_client(mcp_server, principal)
            
            # Execute with timeout
            result = await asyncio.wait_for(
                mcp_client.execute(tool, parameters),
                timeout=30.0
            )
            
            execution_time_ms = int((time.time() - start_time) * 1000)
            
            # Update task status
            state["task_results"][task_id] = result
            state["completed_tasks"].append(task_id)
            
            return state
            
        except asyncio.TimeoutError:
            error = f"Timeout after 30 seconds"
            logger.warning(f"Task {task_id} ({mcp_server}/{tool}) timed out")
            state["failed_tasks"].append({"task_id": task_id, "error": error})
            return state
            
        except Exception as e:
            log_exception(logger, e, context=f"Execution failed for task {task_id} ({mcp_server}/{tool})")
            error = str(e)
            state["failed_tasks"].append({"task_id": task_id, "error": error})
            return state
    
    async def execute_batch(self, state: AgentState, tasks: List[Dict]) -> AgentState:
        """
        Execute multiple tasks concurrently.
        """
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[self.execute_task(state, task) for task in tasks],
            return_exceptions=True
        )
        
        # Merge results
        for result in results:
            if isinstance(result, Exception):
                continue
            state = result
        
        return state

def create_action_node(mcp_registry: MCPRegistry, user_repo: UserRepository, audit_repo: AuditRepository):
    """Create Action Agent node for LangGraph."""
    agent = ActionAgent(mcp_registry, user_repo, audit_repo)
    
    async def action_node(state: AgentState) -> AgentState:
        tasks = state.get("tasks", [])
        if tasks:
            state = await agent.execute_batch(state, tasks)
        return state
    
    return action_node