import asyncio
import time
import json
import logging
from typing import Dict, Any, List

from app.utils.logger import log_exception
from app.agents.state import AgentState, TaskStatus
from app.mcp_alt.registry import MCPAltRegistry
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
    
    def __init__(self, mcp_registry: MCPAltRegistry, openrouter: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository, plan_repo: PlanRepository):
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

    def _safe_json_dumps(self, obj: Any) -> str:
        """Safe JSON serialization that handles non-serializable objects."""
        def default(o):
            if hasattr(o, 'dict'):
                return o.dict()
            if hasattr(o, '__dict__'):
                return o.__dict__
            # Handle MCP content types specifically if they aren't caught by the above
            if type(o).__name__ in ['TextContent', 'ImageContent', 'EmbeddedRes']:
                return {k: v for k, v in o.__dict__.items() if not k.startswith('_')}
            return str(o)
            
        return json.dumps(obj, default=default)

    async def _parse_result(self, mcp_server: str, result: Any) -> Any:
        """
        Uses a specialized parser prompt to clean up and structure tool output.
        """
        parser_prompts = {
            "github": ACTION_GITHUB_PARSER_PROMPT,
            "calendar": ACTION_CALENDAR_PARSER_PROMPT,
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
                    {"role": "user", "content": f"Parse and structure this raw tool result:\n{self._safe_json_dumps(result)}"},
                ],
                temperature=0.1,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            parsed_content = response["choices"][0]["message"]["content"]
            logger.info(f"Action agent parsed result for {mcp_server}: {parsed_content}")
            return json.loads(parsed_content)
        except Exception as e:
            logger.error(f"Failed to parse result for {mcp_server}: {e}")
            return result # Fallback to raw result

    def _resolve_path(self, data: Any, path: str) -> Any:
        """Resolve a dot-notated path in a nested structure (dict/list)."""
        import re
        parts = path.split('.')
        curr = data
        for part in parts:
            if curr is None:
                break
                
            # Handle array indexing like 'items[0]'
            match = re.match(r'(\w+)\[(\d+)\]', part)
            if match:
                name, idx = match.groups()
                if isinstance(curr, dict):
                    curr = curr.get(name)
                if isinstance(curr, list) and int(idx) < len(curr):
                    curr = curr[int(idx)]
                else:
                    curr = None
            elif isinstance(curr, dict):
                curr = curr.get(part)
            elif isinstance(curr, list):
                try:
                    curr = curr[int(part)]
                except (ValueError, IndexError):
                    curr = None
            else:
                curr = None
        return curr

    def _substitute_placeholders(self, value: Any, state: AgentState, plan_tasks: List[Dict] = None) -> Any:
        """Recursively substitute {{...}} placeholders in parameters."""
        import re
        
        if isinstance(value, dict):
            return {k: self._substitute_placeholders(v, state, plan_tasks) for k, v in value.items()}
        if isinstance(value, list):
            return [self._substitute_placeholders(v, state, plan_tasks) for v in value]
        if not isinstance(value, str):
            return value

        # 1. Handle {{user_context.KEY}}
        def replace_context(match):
            path = match.group(1).strip()
            result = self._resolve_path(state.get("user_context", {}), path)
            if result is None:
                logger.warning(f"Context value missing for placeholder: {match.group(0)}. Context: {state.get('user_context')}")
                return "" # Return empty string instead of the placeholder
            return str(result)
        
        logger.debug(f"Substituting in value: {value}")
        value = re.sub(r'\{\{\s*user_context\.([\w\.]+)\s*\}\}', replace_context, value)

        # 2. Handle {{task_X_output.PATH}}
        def replace_output(match):
            task_ref = match.group(1)
            path = match.group(2)
            
            # Find the actual task_id for this reference
            target_task_id = None
            if plan_tasks:
                for t in plan_tasks:
                    if t.get("original_task_id") == task_ref or t.get("task_id") == task_ref:
                        target_task_id = t["task_id"]
                        break
            
            if not target_task_id:
                # Fallback to direct lookup in results by ID
                target_task_id = task_ref

            result_data = state.get("task_results", {}).get(target_task_id)
            if result_data is not None:
                extracted = self._resolve_path(result_data, path) if path else result_data
                if extracted is not None:
                    # If the placeholder is the ENTIRE string and extracted is a complex type, return it directly
                    if match.group(0) == value and not isinstance(extracted, (str, int, float, bool)):
                        return extracted
                    return str(extracted)
            
            return match.group(0)

        # Updated regex to handle task_X_output or task_UUID_output
        # Pattern: {{task_([^_]+)_output(?:\.(.+))?}}
        value = re.sub(r'\{\{task_([^_]+)_output(?:\.([\w\.\[\]]+))?\}\}', replace_output, value)
        
        return value

    async def execute_task(self, state: AgentState, task: Dict) -> AgentState:
        """
        Execute a single task via MCP server.
        """
        task_id = task["task_id"]
        mcp_server = task["mcp_server"]
        tool = task["tool"]
        
        # Get full plan tasks for dependency resolution
        plan_id = state.get("plan_id")
        plan_tasks = []
        if plan_id:
            plan = await redis_client.get_json(f"plan:{plan_id}")
            if not plan:
                plan = await self.plan_repo.get(plan_id)
            if plan:
                plan_tasks = plan.get("tasks", [])

        # Substitute placeholders in parameters
        raw_parameters = task.get("arguments", task.get("parameters", {}))
        parameters = self._substitute_placeholders(raw_parameters, state, plan_tasks)
        
        logger.info(f"Executing task {task_id} ({mcp_server}/{tool}) with params: {parameters}")
        
        # Validation Gate (Tool Contract Enforcement)
        schema_info = self.mcp_registry.get_tool_schema(mcp_server, tool)
        if schema_info:
            from jsonschema import validate, ValidationError
            try:
                # The schema is in schema_info["parameters"]
                validate(instance=parameters, schema=schema_info["parameters"])
                logger.info(f"Task {task_id} passed validation")
            except ValidationError as e:
                error = f"Tool argument mismatch for {mcp_server}/{tool}: {e.message}"
                logger.error(error)
                await self._update_status(state, task_id, "failed", error=error)
                state["failed_tasks"].append({"task_id": task_id, "error": error})
                return state
        
        try:
            # Get principal (user_id for credential lookup)
            principal = state.get("user_id")
            
            # Execute via mcp_alt_registry
            result = await asyncio.wait_for(
                self.mcp_registry.invoke_tool(
                    server_id=mcp_server,
                    tool_name=tool,
                    arguments=parameters,
                    user_id=str(principal) if principal else None
                ),
                timeout=30.0
            )
            
            # Parse/summarize result using specialized prompts
            parsed_result = await self._parse_result(mcp_server, result)
            
            # Update task status to completed
            await self._update_status(state, task_id, "completed", result=parsed_result)
            if task_id not in state["completed_tasks"]:
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

def create_action_node(mcp_registry: MCPAltRegistry, openrouter: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
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