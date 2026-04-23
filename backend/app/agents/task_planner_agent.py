from typing import List, Dict, Any, Set
from collections import deque
import uuid
import json
import re
from datetime import datetime

from app.agents.state import AgentState, Task, TaskStatus
from app.db.repositories.plan_repository import PlanRepository
from app.db.repositories.user_repository import UserRepository
from app.db.repositories.audit_repository import AuditRepository
from app.services.cache_service import redis_client
from app.core.openrouter import OpenRouterClient
from app.core.prompts import MANAGER_TASK_DECOMPOSER_PROMPT

class TaskPlannerAgent:
    """
    Task Planner Agent: Creates and manages task execution plans.
    Uses an LLM for dynamic task decomposition and rule-based logic for dependency tracking.
    """

    def __init__(self, plan_repo: PlanRepository, openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
        self.plan_repo = plan_repo
        self.openrouter = openrouter_client
        self.user_repo = user_repo
        self.audit_repo = audit_repo

    async def create_plan(self, state: AgentState) -> AgentState:
        """
        Create execution plan from validated intent.
        """
        intent = state["validated_intent"]

        # Decompose intent into tasks using the LLM
        tasks = await self._decompose_intent_with_llm(intent, state["user_id"])

        # Validate dependencies
        all_task_ids = {task["task_id"] for task in tasks}
        for task in tasks:
            # Ensure depends_on is a list
            if "depends_on" not in task:
                task["depends_on"] = []
            
            # Generate task_id for each dependency reference
            for i, dep_ref in enumerate(task["depends_on"]):
                # Assuming dep_ref is the "step" number
                try:
                    dep_step = int(dep_ref)
                    # Find the task with that step number
                    for t in tasks:
                        if t.get("step") == dep_step:
                            task["depends_on"][i] = t["task_id"]
                            break
                except (ValueError, IndexError):
                    raise ValueError(f"Task {task['task_id']} has an invalid dependency reference: {dep_ref}")

            for dep_id in task.get("depends_on", []):
                if dep_id not in all_task_ids:
                    raise ValueError(f"Task {task['task_id']} depends on unknown task {dep_id}")

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
            state["final_response"] = "Plan execution completed"

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
            # Find the nodes that are part of the cycle
            cycle_nodes = {k for k, v in in_degree.items() if v > 0}
            raise ValueError(f"Circular dependency detected in tasks: {cycle_nodes}")

        return order

    async def _decompose_intent_with_llm(self, intent: Dict, user_id: str) -> List[Dict]:
        """
        Decompose intent into tasks using the LLM.
        """
        prompt = MANAGER_TASK_DECOMPOSER_PROMPT.replace("{{current_date}}", datetime.now().isoformat())
        
        response = await self.openrouter.complete(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": json.dumps(intent, indent=2)}
            ],
            temperature=0.2,
            max_tokens=2000
        )

        content = response["choices"][0]["message"]["content"]
        
        # Extract JSON from the response
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if not json_match:
            raise ValueError("Invalid format from LLM: no JSON block found")

        try:
            tasks_data = json.loads(json_match.group(1))
            
            # Assign a UUID to each task
            for task in tasks_data:
                task["task_id"] = str(uuid.uuid4())
                
            return tasks_data
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to decode JSON from LLM response: {e}")

def create_task_planner_node(plan_repo: PlanRepository, openrouter_client: OpenRouterClient, user_repo: UserRepository, audit_repo: AuditRepository):
    """Create Task Planner node for LangGraph."""
    agent = TaskPlannerAgent(plan_repo, openrouter_client, user_repo, audit_repo)

    async def task_planner_node(state: AgentState) -> AgentState:
        if not state.get("plan_id"):
            state = await agent.create_plan(state)
        else:
            state = await agent.get_next_tasks(state)
            state = await agent.verify_completion(state)
        return state

    return task_planner_node