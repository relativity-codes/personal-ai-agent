import asyncio
import time
import json
import logging
from typing import Dict, Any, List

from app.utils.logger import log_exception
from app.agents.state import AgentState, TaskStatus
from app.mcp.base import MCPRegistry
from app.services.cache_service import redis_client
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository
from app.db.repositories.plan_repository import PlanRepository
from app.core.openrouter import OpenRouterClient
from app.core.prompts import (
    ACTION_GITHUB_PARSER_PROMPT,
    ACTION_CALENDAR_PARSER_PROMPT,
    ACTION_NOTION_PARSER_PROMPT,
    ACTION_GMAIL_PARSER_PROMPT
)

logger = logging.getLogger(__name__)

class ActionAgent:
    """
    Action Agent: Executes MCP server calls and updates task status.
    """
    
    def __init__(self, mcp_registry: MCPRegistry, openrouter: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository, plan_repo: PlanRepository):
        self.mcp_registry = mcp_registry
        self.openrouter = openrouter
        self.user_repo = user_repo
        self.audit_repo = audit_repo
        self.plan_repo = plan_repo
    
    async def _update_status(self, state: AgentState, task_id: str, status: str, result: Any = None, error: str = None):
        """Update task status in state, DB, and cache."""
        plan_id = state.get("plan_id")
        
        # Update local state
        state["task_status"][task_id] = status
        if result is not None:
            state["task_results"][task_id] = result
        if error:
            state["task_errors"][task_id] = error
            
        if plan_id:
            # Update DB
            await self.plan_repo.update_task_status(
                plan_id=plan_id,
                task_id=task_id,
                status=status,
                result=result,
                error=error
            )
            
            # Update Redis cache
            plan = await redis_client.get_json(f"plan:{plan_id}")
            if plan:
                plan["task_status"][task_id] = status
                if result is not None:
                    plan["task_results"][task_id] = result
                if error:
                    plan["task_errors"][task_id] = error
                await redis_client.set_json(f"plan:{plan_id}", plan, ttl=3600)

    async def _parse_result(self, mcp_server: str, result: Any) -> Any:
        """
        Uses a specialized parser prompt to clean up and structure tool output.
        """
        parser_prompts = {
            "github": ACTION_GITHUB_PARSER_PROMPT,
            "google_calendar": ACTION_CALENDAR_PARSER_PROMPT,
            "notion": ACTION_NOTION_PARSER_PROMPT,
            "gmail": ACTION_GMAIL_PARSER_PROMPT,
        }
        
        prompt = parser_prompts.get(mcp_server)
        if not prompt:
            logger.info(f"No specialized parser for {mcp_server}, returning raw result")
            return result

        try:
            response = await self.openrouter.complete(
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": f"Parse and structure this raw tool result:\n{json.dumps(result)}"},
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            parsed_content = response["choices"][0]["message"]["content"]
            return json.loads(parsed_content)
        except Exception as e:
            logger.error(f"Failed to parse result for {mcp_server}: {e}")
            return result # Fallback to raw result

    async def execute_task(self, state: AgentState, task: Dict) -> AgentState:
        """
        Execute a single task via MCP server.
        """
        task_id = task["task_id"]
        mcp_server = task["mcp_server"]
        tool = task["tool"]
        parameters = task.get("arguments", task.get("parameters", {}))
        
        start_time = time.time()
        
        try:
            # Get MCP client for user
            principal = state.get("google_id") or state.get("user_id")
            mcp_client = self.mcp_registry.get_client(mcp_server, str(principal))
            
            # Execute with timeout
            result = await asyncio.wait_for(
                mcp_client.execute(tool, parameters),
                timeout=30.0
            )
            
            # Parse/summarize result using specialized prompts
            parsed_result = await self._parse_result(mcp_server, result)
            
            # Update task status to completed
            await self._update_status(state, task_id, "completed", result=parsed_result)
            state["completed_tasks"].append(task_id)
            
            return state
            
        except asyncio.TimeoutError:
            error = f"Timeout after 30 seconds"
            logger.warning(f"Task {task_id} ({mcp_server}/{tool}) timed out")
            await self._update_status(state, task_id, "failed", error=error)
            state["failed_tasks"].append({"task_id": task_id, "error": error})
            return state
            
        except Exception as e:
            log_exception(logger, e, context=f"Execution failed for task {task_id} ({mcp_server}/{tool})")
            error = str(e)
            await self._update_status(state, task_id, "failed", error=error)
            state["failed_tasks"].append({"task_id": task_id, "error": error})
            return state
    
    async def execute_batch(self, state: AgentState, tasks: List[Dict]) -> AgentState:
        """
        Execute multiple tasks concurrently.
        """
        # We need a copy of tasks because we'll be modifying the state
        tasks_to_run = list(tasks)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(
            *[self.execute_task(state, task) for task in tasks_to_run],
            return_exceptions=True
        )
        
        # In LangGraph, the last returned state wins or they are merged if using Reducers
        # Since we are passing 'state' to each execute_task and they modify it, 
        # we need to be careful with concurrency if state was a shared mutable object.
        # But here 'state' is a dict, and asyncio.gather runs them.
        # However, it's better to return the final state.
        
        return state

def create_action_node(mcp_registry: MCPRegistry, openrouter: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
    """Create Action Agent node for LangGraph."""
    # We need PlanRepository here
    from app.db.repositories.plan_repository import PlanRepository
    plan_repo = PlanRepository()
    agent = ActionAgent(mcp_registry, openrouter, user_repo, audit_repo, plan_repo)
    
    async def action_node(state: AgentState) -> AgentState:
        tasks = state.get("tasks", [])
        if tasks:
            # Clear tasks from state so they aren't re-run by mistake
            state["tasks"] = []
            state = await agent.execute_batch(state, tasks)
        return state
    
    return action_node