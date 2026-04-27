# Engineering Design Document
## Multi-Agent Personal AI System - Monorepo Structure
### FastAPI + LangGraph + Next.js + Redis + PostgreSQL

---

## Document Control

| Version | Date | Author | Status | Changes |
|---------|------|--------|--------|---------|
| 3.0 | 2026-04-21 | System Architect | Final | Monorepo structure with FastAPI, LangGraph, Next.js, Redis, PostgreSQL |

---

## 1. Executive Summary

### 1.1 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 14 (App Router) | UI, prompt input, streaming responses |
| **Backend** | FastAPI (Python 3.11+) | Agent orchestration, API endpoints |
| **Agent Framework** | LangGraph | Stateful multi-agent workflows |
| **Database** | PostgreSQL (via SQLAlchemy + asyncpg) | User preferences, audit logs, session persistence |
| **Cache/State** | Redis | Agent state, task planning state, rate limiting |
| **AI Gateway** | OpenRouter | LLM access (Claude, GPT-4o, Llama) |
| **MCP Servers** | Python modules | GitHub, Notion, Calendar, Gmail integration |
| **Auth** | Clerk | User authentication, session management |

### 1.2 Project Structure

```
personal-ai-agent/
├── frontend/                 # Next.js application
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
├── backend/                  # FastAPI application
│   ├── app/
│   │   ├── agents/          # LangGraph agents
│   │   ├── api/             # FastAPI routes
│   │   ├── core/            # Core business logic
│   │   ├── db/              # Database models & repositories
│   │   ├── mcp/             # MCP server implementations
│   │   ├── services/        # Service layer
│   │   └── utils/           # Utilities
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
├── .env
├── .gitignore
└── README.md
```

---

## 2. Backend Architecture (FastAPI + LangGraph)

### 2.1 Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application entrypoint
│   ├── config.py                  # Configuration management
│   │
│   ├── agents/                    # LangGraph agents
│   │   ├── __init__.py
│   │   ├── intent_agent.py        # Intent Agent (LangGraph node)
│   │   ├── managerial_agent.py    # Managerial Agent (LangGraph graph)
│   │   ├── task_planner_agent.py  # Task Planner Agent (LangGraph node)
│   │   ├── action_agent.py        # Action Agent (LangGraph node)
│   │   └── state.py               # Agent state definitions
│   │
│   ├── api/                       # FastAPI routes
│   │   ├── __init__.py
│   │   ├── deps.py                # Dependencies (auth, db)
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py            # Chat endpoints
│   │   │   ├── agents.py          # Agent status endpoints
│   │   │   ├── mcp.py             # MCP connection endpoints
│   │   │   └── webhooks.py        # Webhook endpoints
│   │   └── websocket/
│   │       └── chat.py            # WebSocket for streaming
│   │
│   ├── core/                      # Core business logic
│   │   ├── __init__.py
│   │   ├── openrouter.py          # OpenRouter client
│   │   ├── prompts.py             # Prompt templates
│   │   └── security.py            # Security utilities
│   │
│   ├── db/                        # Database layer
│   │   ├── __init__.py
│   │   ├── session.py             # SQLAlchemy async session
│   │   ├── base.py                # Declarative base
│   │   ├── models/                # SQLAlchemy models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── session.py
│   │   │   ├── plan.py
│   │   │   ├── task.py
│   │   │   └── audit_log.py
│   │   └── repositories/          # Data access layer
│   │       ├── __init__.py
│   │       ├── user_repository.py
│   │       ├── plan_repository.py
│   │       └── audit_repository.py
│   │
│   ├── mcp/                       # MCP Server implementations
│   │   ├── __init__.py
│   │   ├── base.py                # Base MCP server class
│   │   ├── github.py              # GitHub MCP server
│   │   ├── notion.py              # Notion MCP server
│   │   ├── calendar.py            # Google Calendar MCP server
│   │   └── gmail.py               # Gmail MCP server
│   │
│   ├── services/                  # Service layer
│   │   ├── __init__.py
│   │   ├── cache_service.py       # Redis cache service
│   │   ├── mcp_registry.py        # MCP server registry
│   │   └── webhook_service.py     # Webhook processing
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── logger.py              # Structured logging
│       ├── metrics.py             # Metrics collection
│       └── validators.py          # Input validation
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Pytest fixtures
│   ├── unit/
│   │   ├── test_intent_agent.py
│   │   ├── test_task_planner.py
│   │   └── test_action_agent.py
│   ├── integration/
│   │   ├── test_api.py
│   │   └── test_mcp.py
│   └── e2e/
│       └── test_flow.py
│
├── alembic/                       # Database migrations
│   └── versions/
│
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── .env.example
└── .python-version
```

### 2.2 Core Implementation Files

#### 2.2.1 Main Application Entrypoint

```python
# backend/app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging

from app.api.v1 import chat, agents, mcp, webhooks
from app.api.websocket import chat as ws_chat
from app.core.openrouter import OpenRouterClient
from app.core.config import settings
from app.db.session import init_db, close_db
from app.services.cache_service import redis_client
from app.services.mcp_registry import mcp_registry
from app.agents.managerial_agent import create_managerial_graph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up...")
    
    # Initialize database connection pool
    await init_db()
    
    # Initialize Redis connection
    await redis_client.connect()
    
    # Initialize OpenRouter client
    app.state.openrouter = OpenRouterClient(
        api_key=settings.OPENROUTER_API_KEY,
        base_url=settings.OPENROUTER_BASE_URL
    )
    
    # Initialize MCP registry
    await mcp_registry.initialize()
    
    # Initialize LangGraph agent
    app.state.managerial_graph = create_managerial_graph()
    
    logger.info("Startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await close_db()
    await redis_client.disconnect()
    logger.info("Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="Personal AI Agent API",
    version="3.0.0",
    description="Multi-Agent Personal AI System with LangGraph",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

# Include routers
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(ws_chat.router, prefix="/ws", tags=["websocket"])

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "3.0.0",
        "services": {
            "database": await _check_db(),
            "redis": await _check_redis()
        }
    }

async def _check_db():
    """Check database connectivity."""
    try:
        from app.db.session import async_session_factory
        async with async_session_factory() as session:
            await session.execute("SELECT 1")
        return "connected"
    except Exception as e:
        return f"error: {str(e)}"

async def _check_redis():
    """Check Redis connectivity."""
    try:
        await redis_client.ping()
        return "connected"
    except Exception as e:
        return f"error: {str(e)}"
```

#### 2.2.2 Configuration

```python
# backend/app/config.py
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    """Application settings."""
    
    # App
    APP_NAME: str = "Personal AI Agent"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    
    # Database (PostgreSQL)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "personal_ai_agent"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    
    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "anthropic/claude-3.5-sonnet"
    OPENROUTER_FALLBACK_MODELS: List[str] = ["openai/gpt-4o", "meta-llama/llama-3-70b-instruct"]
    
    # Clerk Auth
    CLERK_SECRET_KEY: str
    CLERK_PUBLISHABLE_KEY: str
    CLERK_WEBHOOK_SECRET: str
    
    # MCP Server Credentials
    MY_GITHUB_CLIENT_ID: Optional[str] = None
    MY_GITHUB_CLIENT_SECRET: Optional[str] = None
    
    NOTION_CLIENT_ID: Optional[str] = None
    NOTION_CLIENT_SECRET: Optional[str] = None
    
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # seconds
    
    # Task Execution
    MAX_TASKS_PER_REQUEST: int = 10
    TASK_TIMEOUT_SECONDS: int = 30
    MAX_EXECUTION_ITERATIONS: int = 50
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### 2.2.3 Database Models (SQLAlchemy)

```python
# backend/app/db/models/user.py
from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    clerk_id = Column(String(255), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255))
    avatar_url = Column(String(500))
    
    # Preferences
    default_github_repo = Column(String(255))
    default_notion_db = Column(String(255))
    timezone = Column(String(50), default="UTC")
    working_hours_start = Column(String(5), default="09:00")
    working_hours_end = Column(String(5), default="17:00")
    
    # MCP tokens (encrypted)
    mcp_tokens = Column(JSON, default=dict)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    plans = relationship("ExecutionPlan", back_populates="user", cascade="all, delete-orphan")
```

```python
# backend/app/db/models/plan.py
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base

class ExecutionPlan(Base):
    __tablename__ = "execution_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(255), nullable=False, index=True)
    
    intent_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    
    # Task data
    tasks = Column(JSON, nullable=False)  # List of tasks
    task_status = Column(JSON, default=dict)  # task_id -> status
    task_results = Column(JSON, default=dict)
    task_errors = Column(JSON, default=dict)
    
    execution_order = Column(JSON, default=list)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User", back_populates="plans")
```

```python
# backend/app/db/models/audit_log.py
from sqlalchemy import Column, String, DateTime, JSON, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from app.db.base import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    action = Column(String(50), nullable=False)  # chat_request, mcp_connect, etc.
    input_text = Column(String(5000))
    intent_type = Column(String(50))
    plan_id = Column(UUID(as_uuid=True))
    
    success = Column(Boolean, default=True)
    error_message = Column(String(500))
    
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    
    metadata = Column(JSON, default=dict)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
```

#### 2.2.4 LangGraph Agent Implementation

```python
# backend/app/agents/state.py
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
```

```python
# backend/app/agents/intent_agent.py
from langgraph.graph import StateGraph, END
from typing import Dict, Any
import json
import re

from app.agents.state import AgentState
from app.core.openrouter import OpenRouterClient
from app.core.prompts import INTENT_CLASSIFIER_PROMPT, INTENT_VALIDATOR_PROMPT

class IntentAgent:
    """
    Intent Agent: Classifies and validates user input.
    """
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.openrouter = openrouter_client
    
    async def classify_intent(self, state: AgentState) -> AgentState:
        """
        Classify user input into structured intent.
        """
        user_input = state["user_input"]
        
        # Prepare prompt with context
        prompt = INTENT_CLASSIFIER_PROMPT.replace("{{current_date}}", "2026-04-21")
        
        response = await self.openrouter.complete(
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.2,
            max_tokens=500
        )
        
        content = response["choices"][0]["message"]["content"]
        
        # Extract JSON
        json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        
        intent_data = json.loads(content)
        
        state["validated_intent"] = intent_data
        state["intent_confidence"] = intent_data.get("confidence", 0.5)
        state["needs_clarification"] = intent_data.get("confidence", 1.0) < 0.7
        state["clarification_question"] = intent_data.get("clarification_needed")
        
        return state
    
    async def validate_intent(self, state: AgentState) -> AgentState:
        """
        Validate intent and handle low confidence cases.
        """
        if not state["needs_clarification"]:
            return state
        
        # For low confidence, we can ask clarifying questions
        # This would be handled by the Managerial Agent
        return state

def create_intent_node(openrouter_client: OpenRouterClient):
    """Create Intent Agent node for LangGraph."""
    agent = IntentAgent(openrouter_client)
    
    async def intent_node(state: AgentState) -> AgentState:
        state = await agent.classify_intent(state)
        state = await agent.validate_intent(state)
        return state
    
    return intent_node
```

```python
# backend/app/agents/task_planner_agent.py
from typing import List, Dict, Any, Set
from collections import deque
import uuid
from datetime import datetime

from app.agents.state import AgentState, Task, TaskStatus
from app.db.repositories.plan_repository import PlanRepository
from app.services.cache_service import redis_client

class TaskPlannerAgent:
    """
    Task Planner Agent: Creates and manages task execution plans.
    Uses rule-based logic (no LLM) for dependency tracking.
    """
    
    def __init__(self, plan_repo: PlanRepository):
        self.plan_repo = plan_repo
    
    async def create_plan(self, state: AgentState) -> AgentState:
        """
        Create execution plan from validated intent.
        """
        intent = state["validated_intent"]
        
        # Decompose intent into tasks (using LLM via Managerial Agent)
        # For now, we'll create a simple plan based on intent type
        tasks = await self._decompose_intent(intent, state["user_id"])
        
        # Validate dependencies
        all_task_ids = {task["task_id"] for task in tasks}
        for task in tasks:
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
            "execution_order": execution_order
        }
        
        await self.plan_repo.create(plan_data)
        
        # Cache plan in Redis for fast access
        await redis_client.set_json(f"plan:{plan_id}", plan_data, ttl=3600)
        
        state["plan_id"] = plan_id
        state["tasks"] = tasks
        state["task_status"] = {task["task_id"]: TaskStatus.PENDING for task in tasks}
        state["execution_order"] = execution_order
        state["current_task_index"] = 0
        
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
            
            # Skip if already completed or failed
            if task_status.get(task_id) in ["completed", "failed", "in_progress"]:
                continue
            
            # Check dependencies
            dependencies = task.get("depends_on", [])
            deps_completed = all(
                task_status.get(dep_id) == "completed"
                for dep_id in dependencies
            )
            
            if deps_completed:
                executable_tasks.append(task)
        
        state["tasks"] = executable_tasks
        
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
        
        # Update in Redis
        plan = await redis_client.get_json(f"plan:{plan_id}")
        if plan:
            plan["task_status"][task_id] = status.value
            if result:
                plan["task_results"][task_id] = result
            if error:
                plan["task_errors"][task_id] = error
            await redis_client.set_json(f"plan:{plan_id}", plan, ttl=3600)
        
        # Update in PostgreSQL
        await self.plan_repo.update_task_status(plan_id, task_id, status.value, result, error)
        
        if status == TaskStatus.COMPLETED:
            state["completed_tasks"].append(task_id)
        elif status == TaskStatus.FAILED:
            state["failed_tasks"].append({"task_id": task_id, "error": error})
        
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
            raise ValueError("Circular dependency detected")
        
        return order
    
    async def _decompose_intent(self, intent: Dict, user_id: str) -> List[Dict]:
        """
        Decompose intent into tasks (using LLM via Managerial Agent).
        This is a simplified version - full version uses LLM.
        """
        intent_type = intent.get("intent_type")
        
        if intent_type == "agenda_preparation":
            return [
                {
                    "task_id": str(uuid.uuid4()),
                    "step": 1,
                    "description": "Fetch calendar events",
                    "mcp_server": "calendar",
                    "tool": "fetch_events",
                    "parameters": {"date": "tomorrow"},
                    "depends_on": []
                },
                {
                    "task_id": str(uuid.uuid4()),
                    "step": 2,
                    "description": "Fetch open PRs",
                    "mcp_server": "github",
                    "tool": "list_prs",
                    "parameters": {"state": "open"},
                    "depends_on": []
                },
                {
                    "task_id": str(uuid.uuid4()),
                    "step": 3,
                    "description": "Create agenda in Notion",
                    "mcp_server": "notion",
                    "tool": "create_page",
                    "parameters": {"title": "Standup Agenda"},
                    "depends_on": ["task1", "task2"]
                }
            ]
        elif intent_type == "pr_management":
            return [
                {
                    "task_id": str(uuid.uuid4()),
                    "step": 1,
                    "description": "List open PRs",
                    "mcp_server": "github",
                    "tool": "list_prs",
                    "parameters": {"state": "open"},
                    "depends_on": []
                }
            ]
        else:
            return []

def create_task_planner_node(plan_repo: PlanRepository):
    """Create Task Planner node for LangGraph."""
    agent = TaskPlannerAgent(plan_repo)
    
    async def task_planner_node(state: AgentState) -> AgentState:
        if not state.get("plan_id"):
            state = await agent.create_plan(state)
        else:
            state = await agent.get_next_tasks(state)
            state = await agent.verify_completion(state)
        return state
    
    return task_planner_node
```

```python
# backend/app/agents/action_agent.py
import asyncio
import time
from typing import Dict, Any, List

from app.agents.state import AgentState, TaskStatus
from app.mcp.base import MCPRegistry
from app.services.cache_service import redis_client

class ActionAgent:
    """
    Action Agent: Executes MCP server calls.
    """
    
    def __init__(self, mcp_registry: MCPRegistry):
        self.mcp_registry = mcp_registry
    
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
            mcp_client = self.mcp_registry.get_client(mcp_server, state["user_id"])
            
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
            state["failed_tasks"].append({"task_id": task_id, "error": error})
            return state
            
        except Exception as e:
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

def create_action_node(mcp_registry: MCPRegistry):
    """Create Action Agent node for LangGraph."""
    agent = ActionAgent(mcp_registry)
    
    async def action_node(state: AgentState) -> AgentState:
        tasks = state.get("tasks", [])
        if tasks:
            state = await agent.execute_batch(state, tasks)
        return state
    
    return action_node
```

```python
# backend/app/agents/managerial_agent.py
from langgraph.graph import StateGraph, END
from typing import Literal

from app.agents.state import AgentState
from app.agents.intent_agent import create_intent_node
from app.agents.task_planner_agent import create_task_planner_node
from app.agents.action_agent import create_action_node
from app.core.openrouter import OpenRouterClient
from app.db.repositories.plan_repository import PlanRepository
from app.services.mcp_registry import mcp_registry

def should_continue(state: AgentState) -> Literal["task_planner", "action", "response", END]:
    """
    Determine next step based on current state.
    """
    # Check if we need clarification
    if state.get("needs_clarification"):
        return "response"
    
    # Check if plan is complete
    if state.get("final_response"):
        return END
    
    # Check if we have tasks to execute
    if state.get("tasks"):
        return "action"
    
    # Otherwise, continue planning
    return "task_planner"

def create_managerial_graph() -> StateGraph:
    """
    Create the complete LangGraph for the multi-agent system.
    """
    # Initialize dependencies
    openrouter = OpenRouterClient()
    plan_repo = PlanRepository()
    
    # Create nodes
    intent_node = create_intent_node(openrouter)
    task_planner_node = create_task_planner_node(plan_repo)
    action_node = create_action_node(mcp_registry)
    
    # Build graph
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("intent", intent_node)
    workflow.add_node("task_planner", task_planner_node)
    workflow.add_node("action", action_node)
    
    # Set entry point
    workflow.set_entry_point("intent")
    
    # Add edges
    workflow.add_edge("intent", "task_planner")
    workflow.add_conditional_edges(
        "task_planner",
        should_continue,
        {
            "action": "action",
            "task_planner": "task_planner",
            "response": "response",
            END: END
        }
    )
    workflow.add_edge("action", "task_planner")
    
    # Compile
    return workflow.compile()
```

#### 2.2.5 API Endpoints

```python
# backend/app/api/v1/chat.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, AsyncIterator
import json
import asyncio
import uuid

from app.api.deps import get_current_user, get_managerial_graph
from app.agents.state import AgentState

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    stream: bool = False

class ChatResponse(BaseModel):
    content: str
    session_id: str
    metadata: dict

@router.post("/")
async def chat(
    request: ChatRequest,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    graph = Depends(get_managerial_graph)
):
    """
    Send a message to the AI agent.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    # Initialize state
    initial_state: AgentState = {
        "user_id": user["user_id"],
        "session_id": session_id,
        "user_input": request.message,
        "validated_intent": None,
        "intent_confidence": 0.0,
        "needs_clarification": False,
        "clarification_question": None,
        "plan_id": None,
        "tasks": [],
        "task_status": {},
        "execution_order": [],
        "current_task_index": 0,
        "completed_tasks": [],
        "failed_tasks": [],
        "task_results": {},
        "final_response": None,
        "error": None,
        "iteration": 0,
        "max_iterations": 50
    }
    
    # Run the graph
    final_state = await graph.ainvoke(initial_state)
    
    response_content = final_state.get("final_response", "I couldn't process your request.")
    
    return ChatResponse(
        content=response_content,
        session_id=session_id,
        metadata={
            "intent_type": final_state.get("validated_intent", {}).get("intent_type"),
            "plan_id": final_state.get("plan_id"),
            "tasks_completed": len(final_state.get("completed_tasks", [])),
            "tasks_failed": len(final_state.get("failed_tasks", []))
        }
    )

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    user: dict = Depends(get_current_user),
    graph = Depends(get_managerial_graph)
):
    """
    Stream response from the AI agent.
    """
    session_id = request.session_id or str(uuid.uuid4())
    
    async def event_generator() -> AsyncIterator[str]:
        # Initialize state
        initial_state: AgentState = {
            "user_id": user["user_id"],
            "session_id": session_id,
            "user_input": request.message,
            "validated_intent": None,
            "intent_confidence": 0.0,
            "needs_clarification": False,
            "clarification_question": None,
            "plan_id": None,
            "tasks": [],
            "task_status": {},
            "execution_order": [],
            "current_task_index": 0,
            "completed_tasks": [],
            "failed_tasks": [],
            "task_results": {},
            "final_response": None,
            "error": None,
            "iteration": 0,
            "max_iterations": 50
        }
        
        # Emit start event
        yield f"data: {json.dumps({'event': 'start', 'session_id': session_id})}\n\n"
        
        # Stream state updates as they happen
        async for event in graph.astream(initial_state):
            for node_name, node_state in event.items():
                yield f"data: {json.dumps({'event': 'node_complete', 'node': node_name})}\n\n"
                
                if node_state.get("final_response"):
                    response = node_state["final_response"]
                    # Stream response in chunks
                    for i in range(0, len(response), 50):
                        chunk = response[i:i+50]
                        yield f"data: {json.dumps({'event': 'chunk', 'content': chunk})}\n\n"
                        await asyncio.sleep(0.01)
        
        # Emit complete event
        yield f"data: {json.dumps({'event': 'complete'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
```

---

## 3. Frontend Architecture (Next.js)

### 3.1 Directory Structure

```
frontend/
├── app/
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Home page
│   ├── globals.css                # Global styles
│   ├── api/
│   │   └── auth/
│   │       └── webhook/
│   │           └── route.ts       # Clerk webhook handler
│   ├── dashboard/
│   │   └── page.tsx               # Dashboard page
│   ├── settings/
│   │   └── page.tsx               # Settings page
│   └── (auth)/
│       ├── sign-in/[[...sign-in]]/
│       │   └── page.tsx
│       └── sign-up/[[...sign-up]]/
│           └── page.tsx
├── components/
│   ├── chat/
│   │   ├── ChatInterface.tsx      # Main chat component
│   │   ├── ChatMessage.tsx        # Individual message
│   │   ├── ChatInput.tsx          # Input with streaming
│   │   ├── MessageList.tsx        # List of messages
│   │   └── StreamingText.tsx      # Streaming text component
│   ├── dashboard/
│   │   ├── ActivityChart.tsx
│   │   ├── RecentPlans.tsx
│   │   └── StatsCards.tsx
│   ├── settings/
│   │   ├── MCPConnections.tsx     # MCP server connection UI
│   │   ├── Preferences.tsx        # User preferences
│   │   └── ApiKeys.tsx            # API key management
│   └── layout/
│       ├── Header.tsx
│       ├── Sidebar.tsx
│       └── Footer.tsx
├── lib/
│   ├── api/
│   │   ├── client.ts              # API client
│   │   └── types.ts               # API types
│   ├── hooks/
│   │   ├── useChat.ts             # Chat hook with streaming
│   │   ├── useAuth.ts             # Auth hook
│   │   └── useMCPServers.ts       # MCP server hook
│   ├── store/
│   │   ├── chatStore.ts           # Zustand chat store
│   │   └── settingsStore.ts       # Settings store
│   └── utils/
│       ├── markdown.ts            # Markdown rendering
│       └── date.ts                # Date formatting
├── public/
│   └── assets/
├── styles/
│   └── theme.css
├── .env.local
├── next.config.js
├── tailwind.config.js
├── package.json
└── tsconfig.json
```

### 3.2 Core Frontend Components

#### 3.2.1 Chat Interface with Streaming

```tsx
// frontend/components/chat/ChatInterface.tsx
'use client';

import { useState, useRef, useEffect } from 'react';
import { useChat } from '@/lib/hooks/useChat';
import { MessageList } from './MessageList';
import { ChatInput } from './ChatInput';
import { useAuth } from '@clerk/nextjs';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: {
    intent_type?: string;
    plan_id?: string;
    tasks_completed?: number;
  };
}

export function ChatInterface() {
  const { getToken } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);

    // Add placeholder assistant message
    const assistantMessageId = (Date.now() + 1).toString();
    setMessages(prev => [
      ...prev,
      {
        id: assistantMessageId,
        role: 'assistant',
        content: '',
        timestamp: new Date(),
      },
    ]);

    setIsStreaming(true);

    try {
      const token = await getToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
        }),
      });

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No reader available');
      }

      let accumulatedContent = '';
      let metadata: any = {};

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.event === 'start') {
              setSessionId(data.session_id);
            } else if (data.event === 'chunk') {
              accumulatedContent += data.content;
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: accumulatedContent }
                    : msg
                )
              );
            } else if (data.event === 'node_complete') {
              console.log(`Node completed: ${data.node}`);
            } else if (data.event === 'complete') {
              // Final message with metadata
              if (data.metadata) {
                metadata = data.metadata;
              }
            }
          }
        }
      }

      // Update final message with metadata
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, metadata }
            : msg
        )
      );
    } catch (error) {
      console.error('Chat error:', error);
      setMessages(prev =>
        prev.map(msg =>
          msg.id === assistantMessageId
            ? { ...msg, content: 'Sorry, an error occurred. Please try again.' }
            : msg
        )
      );
    } finally {
      setIsStreaming(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <div className="flex-1 overflow-y-auto p-4">
        <MessageList messages={messages} />
        <div ref={messagesEndRef} />
      </div>
      <ChatInput onSend={handleSendMessage} isDisabled={isStreaming} />
    </div>
  );
}
```

#### 3.2.2 Chat Input with Streaming Support

```tsx
// frontend/components/chat/ChatInput.tsx
'use client';

import { useState, KeyboardEvent } from 'react';
import { PaperAirplaneIcon } from '@heroicons/react/24/solid';

interface ChatInputProps {
  onSend: (message: string) => void;
  isDisabled?: boolean;
}

export function ChatInput({ onSend, isDisabled }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSend = () => {
    if (input.trim() && !isDisabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 bg-white p-4">
      <div className="max-w-4xl mx-auto">
        <div className="flex gap-3 items-end">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything... (e.g., 'Prepare for tomorrow's standup')"
            disabled={isDisabled}
            rows={1}
            className="flex-1 resize-none rounded-lg border border-gray-300 p-3 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            style={{ minHeight: '44px', maxHeight: '200px' }}
          />
          <button
            onClick={handleSend}
            disabled={!input.trim() || isDisabled}
            className="rounded-lg bg-blue-600 p-3 text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <PaperAirplaneIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="mt-2 text-xs text-gray-500">
          {isDisabled ? (
            <span className="animate-pulse">AI is thinking...</span>
          ) : (
            <span>Press Enter to send, Shift+Enter for new line</span>
          )}
        </div>
      </div>
    </div>
  );
}
```

#### 3.2.3 Message List Component

```tsx
// frontend/components/chat/MessageList.tsx
'use client';

import { Message } from './ChatInterface';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface MessageListProps {
  messages: Message[];
}

export function MessageList({ messages }: MessageListProps) {
  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {messages.map((message) => (
        <div
          key={message.id}
          className={`flex ${
            message.role === 'user' ? 'justify-end' : 'justify-start'
          }`}
        >
          <div
            className={`max-w-[80%] rounded-lg p-4 ${
              message.role === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-white border border-gray-200'
            }`}
          >
            {message.role === 'assistant' ? (
              <div className="prose prose-sm max-w-none">
                <ReactMarkdown
                  components={{
                    code({ node, inline, className, children, ...props }) {
                      const match = /language-(\w+)/.exec(className || '');
                      return !inline && match ? (
                        <SyntaxHighlighter
                          style={oneDark}
                          language={match[1]}
                          PreTag="div"
                          {...props}
                        >
                          {String(children).replace(/\n$/, '')}
                        </SyntaxHighlighter>
                      ) : (
                        <code className={className} {...props}>
                          {children}
                        </code>
                      );
                    },
                  }}
                >
                  {message.content}
                </ReactMarkdown>
                
                {/* Metadata display */}
                {message.metadata && (
                  <div className="mt-2 text-xs text-gray-500 border-t pt-2">
                    <span className="font-semibold">Intent:</span> {message.metadata.intent_type}
                    {' | '}
                    <span className="font-semibold">Tasks:</span> {message.metadata.tasks_completed} completed
                  </div>
                )}
              </div>
            ) : (
              <div className="whitespace-pre-wrap">{message.content}</div>
            )}
            
            <div
              className={`text-xs mt-2 ${
                message.role === 'user' ? 'text-blue-200' : 'text-gray-400'
              }`}
            >
              {message.timestamp.toLocaleTimeString()}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

#### 3.2.4 API Client

```typescript
// frontend/lib/api/client.ts
import { getToken } from '@clerk/nextjs';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
}

class ApiClient {
  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const token = await getToken();
    
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });
    
    if (!response.ok) {
      const error = await response.text();
      return {
        success: false,
        error: error || `HTTP ${response.status}`,
      };
    }
    
    const data = await response.json();
    return {
      success: true,
      data,
    };
  }
  
  async chat(message: string, sessionId?: string) {
    return this.request('/api/v1/chat', {
      method: 'POST',
      body: JSON.stringify({ message, session_id: sessionId }),
    });
  }
  
  async getMCPServers() {
    return this.request('/api/v1/mcp/servers');
  }
  
  async connectMCPServer(serverName: string) {
    return this.request(`/api/v1/mcp/${serverName}/connect`, {
      method: 'POST',
    });
  }
  
  async getUserPreferences() {
    return this.request('/api/v1/users/preferences');
  }
  
  async updateUserPreferences(preferences: any) {
    return this.request('/api/v1/users/preferences', {
      method: 'PUT',
      body: JSON.stringify(preferences),
    });
  }
  
  async getPlanStatus(planId: string) {
    return this.request(`/api/v1/plans/${planId}/status`);
  }
}

export const apiClient = new ApiClient();
```

#### 3.2.5 Custom Hook for Chat

```typescript
// frontend/lib/hooks/useChat.ts
import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api/client';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface UseChatOptions {
  onStreamChunk?: (chunk: string) => void;
  onComplete?: (fullResponse: string) => void;
  onError?: (error: Error) => void;
}

export function useChat(options: UseChatOptions = {}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  
  const sendMessage = useCallback(async (content: string) => {
    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    
    setIsLoading(true);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/chat/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${await getToken()}`,
        },
        body: JSON.stringify({
          message: content,
          session_id: sessionId,
        }),
      });
      
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      
      if (!reader) throw new Error('No reader');
      
      let assistantContent = '';
      let assistantMessageId = (Date.now() + 1).toString();
      
      // Add placeholder assistant message
      setMessages(prev => [
        ...prev,
        {
          id: assistantMessageId,
          role: 'assistant',
          content: '',
          timestamp: new Date(),
        },
      ]);
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');
        
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));
            
            if (data.event === 'start') {
              setSessionId(data.session_id);
            } else if (data.event === 'chunk') {
              assistantContent += data.content;
              setMessages(prev =>
                prev.map(msg =>
                  msg.id === assistantMessageId
                    ? { ...msg, content: assistantContent }
                    : msg
                )
              );
              options.onStreamChunk?.(data.content);
            } else if (data.event === 'complete') {
              options.onComplete?.(assistantContent);
            }
          }
        }
      }
    } catch (error) {
      console.error('Chat error:', error);
      options.onError?.(error as Error);
      
      setMessages(prev => [
        ...prev,
        {
          id: (Date.now() + 2).toString(),
          role: 'assistant',
          content: 'Sorry, an error occurred. Please try again.',
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, [sessionId, options]);
  
  const clearMessages = useCallback(() => {
    setMessages([]);
    setSessionId(null);
  }, []);
  
  return {
    messages,
    isLoading,
    sessionId,
    sendMessage,
    clearMessages,
  };
}
```

---

## 4. Database Setup (PostgreSQL + Redis)

### 4.1 PostgreSQL Schema (Alembic Migrations)

```python
# backend/alembic/versions/001_initial_schema.py
"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2026-04-21 10:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSON

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('clerk_id', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('default_github_repo', sa.String(255)),
        sa.Column('default_notion_db', sa.String(255)),
        sa.Column('timezone', sa.String(50), server_default='UTC'),
        sa.Column('working_hours_start', sa.String(5), server_default='09:00'),
        sa.Column('working_hours_end', sa.String(5), server_default='17:00'),
        sa.Column('mcp_tokens', JSON, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('is_active', sa.Boolean, default=True)
    )
    
    # Create execution_plans table
    op.create_table(
        'execution_plans',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_id', sa.String(255), nullable=False, index=True),
        sa.Column('intent_type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), server_default='pending'),
        sa.Column('tasks', JSON, nullable=False),
        sa.Column('task_status', JSON, default={}),
        sa.Column('task_results', JSON, default={}),
        sa.Column('task_errors', JSON, default={}),
        sa.Column('execution_order', JSON, default=[]),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now()),
        sa.Column('completed_at', sa.DateTime(timezone=True))
    )
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='SET NULL')),
        sa.Column('action', sa.String(50), nullable=False),
        sa.Column('input_text', sa.String(5000)),
        sa.Column('intent_type', sa.String(50)),
        sa.Column('plan_id', UUID(as_uuid=True)),
        sa.Column('success', sa.Boolean, default=True),
        sa.Column('error_message', sa.String(500)),
        sa.Column('execution_time_ms', sa.Integer),
        sa.Column('tokens_used', sa.Integer),
        sa.Column('metadata', JSON, default={}),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), index=True)
    )
    
    # Create indexes
    op.create_index('idx_audit_logs_user_id', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_logs_created_at', 'audit_logs', ['created_at'])
    op.create_index('idx_execution_plans_user_id', 'execution_plans', ['user_id'])

def downgrade() -> None:
    op.drop_table('audit_logs')
    op.drop_table('execution_plans')
    op.drop_table('users')
```

### 4.2 Redis Key Patterns

```python
# backend/app/services/cache_service.py
import json
from typing import Any, Optional
import redis.asyncio as redis
from app.config import settings

class RedisCache:
    """Redis cache service for agent state and task planning."""
    
    def __init__(self):
        self.client = None
    
    async def connect(self):
        """Connect to Redis."""
        self.client = await redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding='utf-8'
        )
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.client:
            await self.client.close()
    
    async def ping(self) -> bool:
        """Check Redis connectivity."""
        return await self.client.ping()
    
    # Plan state methods
    async def set_plan(self, plan_id: str, plan_data: dict, ttl: int = 3600):
        """Store plan data in Redis."""
        key = f"plan:{plan_id}"
        await self.client.setex(
            key,
            ttl,
            json.dumps(plan_data, default=str)
        )
    
    async def get_plan(self, plan_id: str) -> Optional[dict]:
        """Retrieve plan data from Redis."""
        key = f"plan:{plan_id}"
        data = await self.client.get(key)
        return json.loads(data) if data else None
    
    # Session state methods
    async def set_session(self, session_id: str, user_id: str, data: dict, ttl: int = 86400):
        """Store session data."""
        key = f"session:{session_id}"
        await self.client.hset(key, mapping={
            "user_id": user_id,
            "data": json.dumps(data, default=str),
            "updated_at": str(datetime.utcnow())
        })
        await self.client.expire(key, ttl)
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Retrieve session data."""
        key = f"session:{session_id}"
        data = await self.client.hgetall(key)
        if data:
            data["data"] = json.loads(data["data"])
            return data
        return None
    
    # Rate limiting
    async def check_rate_limit(self, user_id: str, limit: int = 100, period: int = 60) -> bool:
        """Check if user has exceeded rate limit."""
        key = f"rate_limit:{user_id}"
        current = await self.client.get(key)
        
        if current is None:
            await self.client.setex(key, period, 1)
            return True
        
        current_count = int(current)
        if current_count >= limit:
            return False
        
        await self.client.incr(key)
        return True
    
    # Task queue methods
    async def push_pending_task(self, plan_id: str, task_id: str):
        """Add task to pending queue."""
        key = f"plan:{plan_id}:tasks:pending"
        await self.client.rpush(key, task_id)
    
    async def pop_pending_task(self, plan_id: str) -> Optional[str]:
        """Get next pending task."""
        key = f"plan:{plan_id}:tasks:pending"
        return await self.client.lpop(key)
    
    async def add_completed_task(self, plan_id: str, task_id: str):
        """Mark task as completed."""
        key = f"plan:{plan_id}:tasks:completed"
        await self.client.sadd(key, task_id)
    
    async def is_task_completed(self, plan_id: str, task_id: str) -> bool:
        """Check if task is completed."""
        key = f"plan:{plan_id}:tasks:completed"
        return await self.client.sismember(key, task_id)

# Singleton instance
redis_cache = RedisCache()
```

---

## 5. Environment Configuration

### 5.1 Backend .env File

```bash
# backend/.env

# App Configuration
APP_NAME="Personal AI Agent"
APP_ENV="development"
DEBUG=true

# PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=personal_ai_agent

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# OpenRouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_DEFAULT_MODEL=anthropic/claude-3.5-sonnet

# Clerk Authentication
CLERK_SECRET_KEY=sk_xxxxxxxxxxxxx
CLERK_PUBLISHABLE_KEY=pk_xxxxxxxxxxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx

# MCP Server Credentials (Optional - for OAuth)
MY_GITHUB_CLIENT_ID=xxxxxxxxxxxxx
MY_GITHUB_CLIENT_SECRET=xxxxxxxxxxxxx

NOTION_CLIENT_ID=xxxxxxxxxxxxx
NOTION_CLIENT_SECRET=xxxxxxxxxxxxx

GOOGLE_CLIENT_ID=xxxxxxxxxxxxx
GOOGLE_CLIENT_SECRET=xxxxxxxxxxxxx

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_PERIOD=60

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 5.2 Frontend .env.local

```bash
# frontend/.env.local

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_xxxxxxxxxxxxx

CLERK_SECRET_KEY=sk_xxxxxxxxxxxxx
CLERK_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
```

---

## 6. Running the Application

### 6.1 Setup Instructions

```bash
# 1. Clone the repository
git clone <repository-url>
cd personal-ai-agent

# 2. Set up Python virtual environment (Backend)
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Set up Node.js environment (Frontend)
cd ../frontend
npm install

# 4. Configure environment variables
cp backend/.env.example backend/.env
# Edit backend/.env with your credentials

cp frontend/.env.example frontend/.env.local
# Edit frontend/.env.local with your credentials

# 5. Start PostgreSQL (macOS with Homebrew)
brew services start postgresql
# Or run with Docker:
# docker run -d --name postgres -e POSTGRES_PASSWORD=your_password -p 5432:5432 postgres:15

# 6. Start Redis
brew services start redis
# Or run with Docker:
# docker run -d --name redis -p 6379:6379 redis:7-alpine

# 7. Run database migrations (Backend)
cd backend
alembic upgrade head

# 8. Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 9. Start the frontend (in a new terminal)
cd frontend
npm run dev

# 10. Open browser
# Frontend: http://localhost:3000
# API Docs: http://localhost:8000/docs
```

### 6.2 Requirements Files

```txt
# backend/requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
redis==5.0.1
httpx==0.25.1
python-dotenv==1.0.0
langgraph==0.0.20
langchain==0.1.0
clerk-backend-api==0.1.0
python-multipart==0.0.6
email-validator==2.1.0
```

```json
// frontend/package.json
{
  "name": "personal-ai-agent-frontend",
  "version": "1.0.0",
  "private": true,
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start",
    "lint": "next lint"
  },
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@clerk/nextjs": "^4.29.0",
    "@heroicons/react": "^2.0.18",
    "react-markdown": "^9.0.1",
    "react-syntax-highlighter": "^15.5.0",
    "zustand": "^4.4.7",
    "tailwindcss": "^3.3.6",
    "typescript": "^5.3.3"
  },
  "devDependencies": {
    "@types/node": "^20.10.5",
    "@types/react": "^18.2.45",
    "@types/react-syntax-highlighter": "^15.5.11",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.32",
    "eslint": "^8.56.0",
    "eslint-config-next": "14.0.4"
  }
}
```

---

## 7. Testing

### 7.1 Backend Tests (pytest)

```python
# backend/tests/conftest.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_auth():
    return {"user_id": "test_user_123", "email": "test@example.com"}
```

```python
# backend/tests/unit/test_task_planner.py
import pytest
from app.agents.task_planner_agent import TaskPlannerAgent
from app.agents.state import TaskStatus

@pytest.mark.asyncio
async def test_dependency_resolution():
    tasks = [
        {"task_id": "task1", "depends_on": []},
        {"task_id": "task2", "depends_on": []},
        {"task_id": "task3", "depends_on": ["task1", "task2"]}
    ]
    
    order = TaskPlannerAgent._topological_sort(tasks)
    
    assert order.index("task1") < order.index("task3")
    assert order.index("task2") < order.index("task3")

@pytest.mark.asyncio
async def test_circular_dependency_detection():
    tasks = [
        {"task_id": "task1", "depends_on": ["task2"]},
        {"task_id": "task2", "depends_on": ["task1"]}
    ]
    
    with pytest.raises(ValueError, match="Circular dependency"):
        TaskPlannerAgent._topological_sort(tasks)
```

---

## 8. Summary

This engineering document provides a complete, production-ready design for the multi-agent personal AI system with:

- **Backend**: FastAPI + LangGraph for agent orchestration
- **Frontend**: Next.js 14 with real-time streaming
- **Database**: PostgreSQL for persistent storage
- **Cache**: Redis for state management and rate limiting
- **Agents**: Intent, Managerial, Task Planner, and Action agents
- **MCP Servers**: GitHub, Notion, Calendar, Gmail integrations

The system is designed to run without Docker, using local development servers with clear setup instructions.