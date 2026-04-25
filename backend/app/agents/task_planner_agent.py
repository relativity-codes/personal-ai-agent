from typing import List, Dict, Any, Set
from collections import deque
import uuid
import json
import re
import logging
from datetime import datetime

from app.agents.state import AgentState, Task, TaskStatus
from app.db.repositories.plan_repository import PlanRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository
from app.services.cache_service import redis_client
from app.core.openrouter import OpenRouterClient
from app.core.prompts import get_prompt
from app.mcp_alt.registry import MCPAltRegistry
from app.utils.logger import log_exception

logger = logging.getLogger(__name__)

class TaskPlannerAgent:
    """
    Task Planner Agent: Creates and manages task execution plans.
    Uses an LLM for dynamic task decomposition and rule-based logic for dependency tracking.
    """

    def __init__(self, mcp_registry: MCPAltRegistry, plan_repo: PlanRepository, openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
        self.mcp_registry = mcp_registry
        self.plan_repo = plan_repo
        self.openrouter = openrouter_client
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def create_plan(self, state: AgentState) -> AgentState:
        """
        Create execution plan from validated intent.
        """
        try:
            intent = state.get("validated_intent")
            if not intent or state.get("needs_clarification"):
                logger.info("Skipping task planning: intent missing or clarification needed.")
                return state

            # Decompose intent into tasks using the LLM
            tasks = await self._decompose_intent_with_llm(intent, state)
            print(f"DEBUG: tasks={tasks} (type={type(tasks)})")
            logger.info(f"Decomposed intent into {len(tasks)} tasks: {tasks}")

            # Validate dependencies
            all_task_ids = {task["task_id"] for task in tasks}
            for task in tasks:
                # Ensure depends_on is a list
                deps = task.get("depends_on")
                if deps is None:
                    task["depends_on"] = []
                elif not isinstance(deps, list):
                    task["depends_on"] = [deps]
                
                logger.info(f"Task {task.get('step')} depends_on: {task['depends_on']} (type: {type(task['depends_on'])})")
                
                # Generate task_id for each dependency reference
                for i, dep_ref in enumerate(task["depends_on"]):
                    found = False
                    
                    # Try as step number (int)
                    try:
                        dep_step = int(dep_ref)
                        for t in tasks:
                            if t.get("step") == dep_step:
                                if t["task_id"] != task["task_id"]:
                                    task["depends_on"][i] = t["task_id"]
                                    found = True
                                break
                    except (ValueError, TypeError):
                        pass
                    
                    if found:
                        continue
                        
                    # Try as original task_id if it was a string
                    for t in tasks:
                        if t.get("original_task_id") == str(dep_ref):
                            if t["task_id"] != task["task_id"]:
                                task["depends_on"][i] = t["task_id"]
                                found = True
                            break
                    
                    if not found:
                        logger.warning(f"Task {task.get('step')} has an unresolvable dependency: {dep_ref}")
                        # We'll let the next validation step raise the ValueError if it's still missing

                # Filter out self-dependencies and ensure all are known
                valid_deps = []
                for dep_id in task.get("depends_on", []):
                    if dep_id == task["task_id"]:
                        logger.warning(f"Removing self-dependency for task {task['task_id']}")
                        continue
                    if dep_id not in all_task_ids:
                        raise ValueError(f"Task {task['task_id']} depends on unknown task {dep_id}")
                    valid_deps.append(dep_id)
                task["depends_on"] = valid_deps

            # Calculate execution order (topological sort)
            execution_order = self._topological_sort(tasks)

            # Create plan in database
            plan_id = str(uuid.uuid4())
            plan_data = {
                "id": plan_id,
                "user_id": state["user_id"],
                "session_id": state["session_id"],
                "intent_type": intent["intent_type"],
                "tasks": tasks,
                "task_status": {task["task_id"]: "pending" for task in tasks},
                "execution_order": execution_order,
                "task_results": {},
                "task_errors": {}
            }

            await self.plan_repo.create(plan_data)

            # Cache plan in Redis for fast access
            await redis_client.set_json(f"plan:{plan_id}", plan_data, ttl=3600)

            state["plan_id"] = plan_id
            state["tasks"] = tasks
            state["task_status"] = {task["task_id"]: TaskStatus.PENDING for task in tasks}
            state["execution_order"] = execution_order
            state["current_task_index"] = 0
            state["task_results"] = {}
            state["task_errors"] = {}

            return state
        except Exception as e:
            log_exception(logger, e, context=f"Failed to create plan for session {state.get('session_id')}")
            state["error"] = str(e)
            raise e

    async def get_next_tasks(self, state: AgentState) -> AgentState:
        """
        Get next executable tasks (all dependencies completed).
        """
        plan_id = state["plan_id"]

        # Get plan from cache or DB
        plan = await redis_client.get_json(f"plan:{plan_id}")
        if not plan:
            plan = await self.plan_repo.get(plan_id)

        task_status = plan.get("task_status", {})
        tasks = plan.get("tasks", [])

        executable_tasks = []

        for task in tasks:
            task_id = task["task_id"]

            if task_status.get(task_id) in ["completed", "failed", "in_progress"]:
                continue

            dependencies = task.get("depends_on", [])
            deps_completed = all(
                task_status.get(dep_id) == "completed"
                for dep_id in dependencies
            )

            if deps_completed:
                executable_tasks.append(task)
                task_status[task_id] = "in_progress"

        state["tasks"] = executable_tasks
        
        # Update the plan in cache
        if plan:
            plan["task_status"] = task_status
            await redis_client.set_json(f"plan:{plan_id}", plan, ttl=3600)

        return state

    async def update_task_status(
        self,
        state: AgentState,
        task_id: str,
        status: TaskStatus,
        result: Any = None,
        error: str = None
    ) -> AgentState:
        """
        Update task status in the plan.
        """
        plan_id = state["plan_id"]

        plan = await redis_client.get_json(f"plan:{plan_id}")
        if not plan:
            plan = await self.plan_repo.get(plan_id)

        if plan:
            plan["task_status"][task_id] = status.value
            if result:
                plan["task_results"][task_id] = result
            if error:
                plan["task_errors"][task_id] = error
            await redis_client.set_json(f"plan:{plan_id}", plan, ttl=3600)

        await self.plan_repo.update_task_status(plan_id, task_id, status.value, result, error)

        if status == TaskStatus.COMPLETED:
            state["completed_tasks"].append(task_id)
            state["task_results"][task_id] = result
        elif status == TaskStatus.FAILED:
            state["failed_tasks"].append({"task_id": task_id, "error": error})
            state["task_errors"][task_id] = error

        state["task_status"][task_id] = status

        return state

    async def verify_completion(self, state: AgentState) -> AgentState:
        """
        Verify if all tasks are completed.
        """
        plan_id = state["plan_id"]
        plan = await redis_client.get_json(f"plan:{plan_id}")

        if not plan:
            plan = await self.plan_repo.get(plan_id)

        task_status = plan.get("task_status", {})

        all_completed = all(
            status in ["completed", "failed"]
            for status in task_status.values()
        )

        if all_completed:
            pass

        return state

    def _topological_sort(self, tasks: List[Dict]) -> List[str]:
        """
        Kahn's algorithm for topological sorting.
        """
        graph = {task["task_id"]: set(task.get("depends_on", [])) for task in tasks}
        in_degree = {task_id: len(deps) for task_id, deps in graph.items()}

        queue = deque([task_id for task_id, degree in in_degree.items() if degree == 0])
        order = []

        while queue:
            task_id = queue.popleft()
            order.append(task_id)

            for other_id, deps in graph.items():
                if task_id in deps:
                    in_degree[other_id] -= 1
                    if in_degree[other_id] == 0:
                        queue.append(other_id)

        if len(order) != len(tasks):
            cycle_nodes = {k for k, v in in_degree.items() if v > 0}
            raise ValueError(f"Circular dependency detected in tasks: {cycle_nodes}")

        return order

    async def _decompose_intent_with_llm(self, intent: Dict, state: AgentState) -> List[Dict]:
        """
        Decompose intent into tasks using the LLM.
        """
        prompt = get_prompt("managerial", "task_decomposer").replace("{{current_date}}", datetime.now().isoformat())
        
        # Add tool catalog to the prompt
        tools = await self.mcp_registry.list_all_tools()
        if tools:
            catalog_str = json.dumps(tools, indent=2)
            prompt = f"{prompt}\n\nTOOL CATALOG (STRICT SCHEMAS):\n{catalog_str}"

        # Add user context to the prompt
        user_context = state.get("user_context", {})
        if user_context:
            context_str = "\n".join([f"{k}: {v}" for k, v in user_context.items() if v])
            prompt = f"{prompt}\n\nUser Context:\n{context_str}"
        
        response = await self.openrouter.complete(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(intent, indent=2)}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        content = response["choices"][0]["message"]["content"]
        
        # Extract JSON from the response - more robust regex
        json_match = re.search(r'```(?:json)?\s*(.*?)\s*```', content, re.DOTALL)
        tasks_json = None
        
        if json_match:
            tasks_json = json_match.group(1)
        else:
            # Fallback: try to find anything that looks like a JSON array
            array_match = re.search(r'(\[.*\])', content, re.DOTALL)
            if array_match:
                tasks_json = array_match.group(1)
            else:
                logger.error(f"Failed to find JSON block in LLM response. Raw content:\n{content}")
                raise ValueError("Invalid format from LLM: no JSON block found")

        try:
            tasks_data = json.loads(tasks_json)
            
            # Handle wrapped format: {"tasks": [...], "execution_order": [...]}
            if isinstance(tasks_data, dict) and "tasks" in tasks_data:
                logger.info("Detected wrapped JSON format from LLM")
                tasks_data = tasks_data["tasks"]
                
            if not isinstance(tasks_data, list):
                # If it's a single dict, wrap it in a list
                if isinstance(tasks_data, dict):
                    tasks_data = [tasks_data]
                else:
                    raise ValueError(f"Expected list of tasks from LLM, got {type(tasks_data).__name__}")
            
            # Assign a UUID to each task, but preserve the original ID for dependency resolution
            for i, task in enumerate(tasks_data):
                orig_id = task.get("task_id")
                task["original_task_id"] = str(orig_id) if orig_id is not None else None
                
                # Normalize arguments/parameters
                if "arguments" not in task and "parameters" in task:
                    task["arguments"] = task["parameters"]
                if "arguments" not in task:
                    task["arguments"] = {}
                
                # Ensure step is an integer and present
                if "step" not in task:
                    if orig_id is not None:
                        try:
                            # Try to extract number from "task_1" or "1"
                            nums = re.findall(r'\d+', str(orig_id))
                            if nums:
                                task["step"] = int(nums[0])
                            else:
                                task["step"] = i + 1
                        except (ValueError, TypeError):
                            task["step"] = i + 1
                    else:
                        task["step"] = i + 1
                else:
                    try:
                        task["step"] = int(task["step"])
                    except (ValueError, TypeError):
                        task["step"] = i + 1
                
                task["task_id"] = str(uuid.uuid4())
                
            return tasks_data
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from LLM response. Error: {e}\nAttempted to parse:\n{tasks_json}")
            raise ValueError(f"Failed to decode JSON from LLM response: {e}")

def create_task_planner_node(mcp_registry: MCPAltRegistry, plan_repo: PlanRepository, openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
    """Create Task Planner node for LangGraph."""
    agent = TaskPlannerAgent(mcp_registry, plan_repo, openrouter_client, user_repo, audit_repo)

    async def task_planner_node(state: AgentState) -> AgentState:
        if not state.get("plan_id"):
            state = await agent.create_plan(state)
        else:
            state = await agent.get_next_tasks(state)
            state = await agent.verify_completion(state)
        return state

    return task_planner_node