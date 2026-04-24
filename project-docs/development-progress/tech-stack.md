# Technology Stack Document
## Personal AI Agent - Multi-Agent System

---

## Document Control

| Version | Date | Author | Status |
|---------|------|--------|--------|
| 1.0 | 2026-04-21 | System Architect | Final |

---

## 1. Executive Summary

This document defines the complete technology stack for the **Personal AI Agent** - a multi-agent system that processes natural language commands and executes workflows across GitHub, Notion, Google Calendar, and Gmail.

### 1.1 Stack Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                    Next.js 14 (React 18)                            │    │
│  │         Tailwind CSS · Clerk Auth · Server Components               │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                               API GATEWAY                                    │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      FastAPI + Uvicorn                               │    │
│  │              Pydantic Validation · OpenAPI Docs                      │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AGENT ORCHESTRATION                                │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                         LangGraph                                    │    │
│  │    Stateful Multi-Agent Workflows · Cycle Management                │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │    Intent    │  │ Managerial   │  │ Task Planner │  │   Action     │     │
│  │    Agent     │  │   Agent      │  │    Agent     │  │    Agent     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                                AI & LLM                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      OpenRouter Gateway                              │    │
│  │   Claude 3.5 Sonnet · GPT-4o · Llama 3 70B · Gemini                 │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA & CACHE                                      │
│  ┌────────────────────────────┐  ┌────────────────────────────────────┐     │
│  │        PostgreSQL          │  │              Redis                 │     │
│  │    (Primary Database)      │  │    (Cache & State Management)      │     │
│  └────────────────────────────┘  └────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           EXTERNAL SERVICES                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │  GitHub  │  │  Notion  │  │ Google   │  │  Gmail   │  │  Clerk   │      │
│  │   API    │  │   API    │  │Calendar  │  │   API    │  │   Auth   │      │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Backend Technologies

### 2.1 Core Framework

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Python** | 3.11+ | Runtime | Async support, rich ecosystem, type hints |
| **FastAPI** | 0.104+ | Web Framework | Async native, automatic OpenAPI docs, Pydantic v2 |
| **Uvicorn** | 0.24+ | ASGI Server | High-performance, production-ready |

**Key Features Used:**
- Async/await for concurrent request handling
- Dependency injection for auth and DB sessions
- Lifespan context managers for startup/shutdown
- WebSocket support for real-time streaming

### 2.2 Agent Framework

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **LangGraph** | 0.0.20+ | Agent Orchestration | Stateful multi-agent workflows, cycle detection |
| **LangChain** | 0.1.0+ | LLM Utilities | Prompt templates, output parsers |

**Why LangGraph over other frameworks:**

| Feature | LangGraph | Custom Implementation |
|---------|-----------|----------------------|
| State management | Built-in | Manual |
| Cycle detection | Automatic | Complex |
| Conditional edges | Native | Custom logic |
| Checkpointing | Supported | Additional work |
| Streaming | First-class | Manual SSE |

### 2.3 Database & Cache

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **PostgreSQL** | 15+ | Primary Database | ACID compliance, JSON support, full-text search |
| **SQLAlchemy** | 2.0+ | ORM | Async support, migration compatibility |
| **asyncpg** | 0.29+ | PostgreSQL Driver | Fastest async driver for Python |
| **Alembic** | 1.12+ | Migrations | Version control for DB schema |
| **Redis** | 7+ | Cache & State | Sub-millisecond latency, data structures |

**PostgreSQL vs Alternatives:**

| Feature | PostgreSQL | SQLite | MySQL |
|---------|------------|--------|-------|
| Async support | ✅ (asyncpg) | ❌ | ✅ (aiomysql) |
| JSON operations | ✅ (excellent) | ✅ (limited) | ✅ (good) |
| Full-text search | ✅ (built-in) | ❌ | ✅ |
| Concurrency | ✅ | ❌ (write locks) | ✅ |
| Production ready | ✅ | ❌ | ✅ |

**Redis Data Structures Used:**
- `String`: Rate limiting counters, session tokens
- `Hash`: Session state, user context
- `List`: Task queues
- `Set`: Completed tasks tracking
- `Sorted Set`: Expiring cache entries

### 2.4 AI & LLM Integration

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **OpenRouter** | API v1 | LLM Gateway | Single API for multiple models, fallback support |
| **httpx** | 0.25+ | HTTP Client | Async, HTTP/2 support |

**Supported Models & Use Cases:**

| Model | Provider | Temperature | Use Case |
|-------|----------|-------------|-----------|
| `claude-3.5-sonnet` | Anthropic | 0.2-0.3 | Intent classification, task decomposition |
| `gpt-4o` | OpenAI | 0.3-0.5 | Response generation, summarization |
| `llama-3-70b` | Meta | 0.5-0.7 | Creative tasks, brainstorming |
| `gemini-pro` | Google | 0.3 | Backup, cost optimization |

**Why OpenRouter over direct API:**

| Feature | OpenRouter | Direct API |
|---------|------------|------------|
| Single API key | ✅ | ❌ (multiple keys) |
| Model fallback | ✅ | ❌ |
| Cost optimization | ✅ | ❌ (manual) |
| Unified response format | ✅ | ❌ (per provider) |
| Rate limiting | ✅ (per key) | ❌ (per model) |

### 2.5 Authentication & Security

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Clerk** | Latest | Auth Platform | Pre-built UI, webhooks, session management |
| **python-jose** | 3.3+ | JWT | Token verification |
| **passlib** | 1.7+ | Password Hashing | bcrypt support |
| **cryptography** | 41+ | Encryption | MCP token encryption |

**Authentication Flow:**

```python
# Clerk webhook handling
@app.post("/api/webhooks/clerk")
async def clerk_webhook(request: Request):
    payload = await request.json()
    event_type = payload.get("type")
    
    if event_type == "user.created":
        # Create user in PostgreSQL
        await create_user(payload["data"])
    elif event_type == "user.deleted":
        # Soft delete user
        await deactivate_user(payload["data"]["id"])
```

### 2.6 MCP (Model Context Protocol) Servers

| MCP Server | Library | Authentication | Rate Limits |
|------------|---------|----------------|-------------|
| **GitHub** | `httpx` | OAuth 2.0 / PAT | 5000 req/hour |
| **Notion** | `httpx` | Integration Token | 3 req/sec |
| **Google Calendar** | `google-api-python-client` | OAuth 2.0 | 10000 req/day |
| **Gmail** | `google-api-python-client` | OAuth 2.0 | 10000 req/day |

**MCP Server Interface:**

```python
# Base MCP Server abstract class
class BaseMCPServer(ABC):
    @abstractmethod
    async def list_tools(self) -> List[Tool]:
        pass
    
    @abstractmethod
    async def call_tool(self, name: str, arguments: dict) -> Any:
        pass
```

---

## 3. Frontend Technologies

### 3.1 Core Framework

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Next.js** | 14.0+ | React Framework | App Router, SSR, API routes |
| **React** | 18.2+ | UI Library | Concurrent features, Server Components |
| **TypeScript** | 5.3+ | Language | Type safety, better DX |
| **Tailwind CSS** | 3.3+ | Styling | Utility-first, rapid development |

**Why Next.js App Router:**

| Feature | App Router | Pages Router |
|---------|------------|--------------|
| Server Components | ✅ | ❌ |
| Streaming | ✅ (built-in) | ❌ (manual) |
| Layout nesting | ✅ (easier) | ✅ (complex) |
| Loading UI | ✅ | ❌ |
| Error boundaries | ✅ | ❌ |

### 3.2 State Management

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Zustand** | 4.4+ | Client State | Minimal boilerplate, TypeScript-first |
| **React Query** | 5.0+ | Server State | Caching, refetching, optimistic updates |
| **React Context** | Built-in | Global State | Theme, auth, notifications |

**State Management Strategy:**

```typescript
// Zustand store for chat state
interface ChatStore {
  messages: Message[];
  isStreaming: boolean;
  sessionId: string | null;
  addMessage: (message: Message) => void;
  setStreaming: (streaming: boolean) => void;
  clearMessages: () => void;
}

// React Query for API data
const { data: plans } = useQuery({
  queryKey: ['plans', userId],
  queryFn: () => fetchPlans(userId),
  staleTime: 30000, // 30 seconds
});
```

### 3.3 UI Components & Styling

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Tailwind CSS** | 3.3+ | Styling | Utility-first, no CSS files |
| **Headless UI** | 1.7+ | Unstyled Components | Accessibility, keyboard navigation |
| **Heroicons** | 2.0+ | Icons | SVG icons, consistent design |
| **React Markdown** | 9.0+ | Markdown | AI responses formatting |
| **Syntax Highlighter** | 15.5+ | Code Blocks | PR diffs, code snippets |

**Design System:**

```css
/* tailwind.config.js */
module.exports = {
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          700: '#1d4ed8',
        },
        secondary: {
          500: '#10b981',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'typing': 'typing 1s ease-in-out infinite',
      },
    },
  },
}
```

### 3.4 Real-time Communication

| Technology | Version | Purpose | Rationale |
|------------|---------|---------|-----------|
| **Server-Sent Events (SSE)** | HTML5 | Streaming Responses | One-way, automatic reconnection |
| **WebSocket** | RFC 6455 | Bidirectional | Future: collaborative features |

**SSE vs WebSocket:**

| Feature | SSE | WebSocket |
|---------|-----|-----------|
| Direction | Server → Client | Bidirectional |
| Reconnection | Automatic | Manual |
| HTTP/2 support | ✅ (multiplexing) | ✅ |
| Browser support | ✅ (all modern) | ✅ |
| Implementation | Simpler | Complex |
| Use case | AI streaming | Real-time collaboration |

---

## 4. Development Tools

### 4.1 Version Control & CI/CD

| Technology | Version | Purpose |
|------------|---------|---------|
| **Git** | 2.40+ | Version control |
| **GitHub Actions** | Latest | CI/CD pipeline |
| **pre-commit** | 3.5+ | Git hooks |
| **commitlint** | 18+ | Commit message validation |

**Git Hooks Configuration:**

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.6
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.7.0
    hooks:
      - id: mypy
        args: [--ignore-missing-imports]
  
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
```

### 4.2 Code Quality

| Technology | Version | Purpose |
|------------|---------|---------|
| **Ruff** | 0.1.6+ | Python linter & formatter (replaces flake8, black, isort) |
| **mypy** | 1.7+ | Static type checking |
| **ESLint** | 8.56+ | TypeScript linting |
| **Prettier** | 3.1+ | Code formatting |
| **pytest** | 7.4+ | Testing framework |

**VS Code Extensions (Recommended):**
- Python (`ms-python.python`)
- Ruff (`charliermarsh.ruff`)
- Tailwind CSS (`bradlc.vscode-tailwindcss`)
- Prettier (`esbenp.prettier-vscode`)

### 4.3 API Development

| Technology | Version | Purpose |
|------------|---------|---------|
| **Postman** | Latest | API testing |
| **OpenAPI/Swagger** | 3.0 | API documentation |
| **HTTPie** | 3.2+ | CLI HTTP client |

**FastAPI Automatic Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 5. Infrastructure & Deployment

### 5.1 Deployment Options

| Option | Backend | Frontend | Database | Cache |
|--------|---------|----------|----------|-------|
| **Local Dev** | Uvicorn | Next.js dev | PostgreSQL (local) | Redis (local) |
| **Production (AWS)** | ECS/Lambda | Vercel | RDS | ElastiCache |
| **Production (Self-hosted)** | Gunicorn + Nginx | Nginx | PostgreSQL | Redis |

### 5.2 Environment Variables

```bash
# Backend (.env)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db
REDIS_URL=redis://localhost:6379/0
OPENROUTER_API_KEY=sk-or-v1-xxx
CLERK_SECRET_KEY=sk_xxx
```

### 5.3 Resource Requirements

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Backend API | 2 cores | 2 GB | 10 GB |
| PostgreSQL | 2 cores | 4 GB | 50 GB+ |
| Redis | 1 core | 1 GB | 10 GB |
| Frontend | 1 core | 512 MB | 5 GB |

---

## 6. Monitoring & Observability

### 6.1 Logging & Metrics

| Technology | Purpose | Use Case |
|------------|---------|----------|
| **Python logging** | Application logs | Structured JSON logs |
| **OpenTelemetry** | Distributed tracing | LangGraph workflow tracing |
| **Prometheus** (optional) | Metrics collection | Request rates, latency |
| **Grafana** (optional) | Visualization | Dashboards |

**Structured Logging Format:**

```json
{
  "timestamp": "2026-04-21T10:00:00Z",
  "level": "INFO",
  "agent": "managerial_agent",
  "request_id": "req_abc123",
  "user_id": "user_456",
  "message": "Processing request",
  "duration_ms": 2450,
  "intent_type": "agenda_preparation"
}
```

### 6.2 Error Tracking

| Technology | Purpose |
|------------|---------|
| **Sentry** (optional) | Error tracking, performance monitoring |
| **Rollbar** (optional) | Real-time error alerts |

---

## 7. Dependencies Summary

### 7.1 Backend Dependencies

```txt
# Core
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
sqlalchemy==2.0.23
asyncpg==0.29.0
alembic==1.12.1
redis==5.0.1

# AI & Agents
langgraph==0.0.20
langchain==0.1.0
httpx==0.25.1

# Auth
clerk-backend-api==0.1.0
python-jose[cryptography]==3.3.0

# Utilities
python-dotenv==1.0.0
email-validator==2.1.0
python-multipart==0.0.6
```

### 7.2 Frontend Dependencies

```json
{
  "dependencies": {
    "next": "14.0.4",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "@clerk/nextjs": "^4.29.0",
    "zustand": "^4.4.7",
    "@tanstack/react-query": "^5.12.0",
    "react-markdown": "^9.0.1",
    "react-syntax-highlighter": "^15.5.0",
    "@heroicons/react": "^2.0.18",
    "@headlessui/react": "^1.7.17",
    "tailwindcss": "^3.3.6"
  },
  "devDependencies": {
    "@types/node": "^20.10.5",
    "@types/react": "^18.2.45",
    "typescript": "^5.3.3",
    "eslint": "^8.56.0",
    "prettier": "^3.1.1"
  }
}
```

---

## 8. Decision Matrix & Rationale

### 8.1 Framework Decisions

| Decision | Options | Selected | Rationale |
|----------|---------|----------|-----------|
| Backend Framework | FastAPI, Django, Flask | **FastAPI** | Async native, OpenAPI, performance |
| Agent Framework | LangGraph, AutoGen, Custom | **LangGraph** | State management, cycle handling |
| Frontend | Next.js, Vite, CRA | **Next.js** | SSR, API routes, streaming |
| Database | PostgreSQL, MongoDB, SQLite | **PostgreSQL** | ACID, JSON support, reliability |
| Cache | Redis, Memcached, In-memory | **Redis** | Data structures, persistence |
| LLM Gateway | OpenRouter, Direct, LiteLLM | **OpenRouter** | Multi-model, fallback, cost control |
| Auth | Clerk, Auth0, Supabase | **Clerk** | Pre-built UI, webhooks, session mgmt |

### 8.2 Trade-offs Analyzed

| Area | Trade-off | Decision |
|------|-----------|----------|
| **Performance vs Complexity** | Redis adds complexity but improves performance | Accept Redis for state management |
| **Flexibility vs Standardization** | Multiple LLM models increase complexity | Use OpenRouter for unified interface |
| **Real-time vs Simplicity** | Streaming responses complex to implement | Implement SSE for AI responses |
| **Type Safety vs Speed** | TypeScript/Pydantic adds dev time but prevents bugs | Prioritize type safety |

---

## 9. Version Strategy

### 9.1 Versioning Scheme

```
MAJOR.MINOR.PATCH
- MAJOR: Incompatible API changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes
```

### 9.2 Current Versions

| Component | Current | Next Planned | EOL |
|-----------|---------|--------------|-----|
| Python | 3.11 | 3.12 (Q2 2024) | 2027 |
| FastAPI | 0.104 | 0.105 | - |
| Next.js | 14.0 | 14.1 | - |
| PostgreSQL | 15 | 16 | 2027 |
| Redis | 7 | 7.2 | 2026 |

### 9.3 Upgrade Policy
- Security patches: Within 48 hours
- Minor version updates: Monthly review
- Major version updates: Quarterly with testing

---

## 10. Security Considerations

### 10.1 Data Encryption

| Data Type | At Rest | In Transit | Method |
|-----------|---------|------------|--------|
| User credentials | ✅ | ✅ | bcrypt + TLS |
| MCP tokens | ✅ | ✅ | AES-256 + TLS |
| Chat history | ✅ | ✅ | TLS |
| Audit logs | ✅ | ✅ | TLS |

### 10.2 API Security

| Layer | Protection | Implementation |
|-------|-----------|----------------|
| Authentication | JWT | Clerk tokens |
| Rate Limiting | Redis | 100 req/min per user |
| Input Validation | Pydantic | Schema validation |
| CORS | Origin checking | Configurable whitelist |
| SQL Injection | ORM | SQLAlchemy parameters |

---

## 11. Development Environment Setup

### 11.1 Quick Start

```bash
# Clone repository
git clone https://github.com/your-org/personal-ai-agent.git
cd personal-ai-agent

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials

# Frontend setup
cd ../frontend
npm install
cp .env.example .env.local
# Edit .env.local with your credentials

# Start services
# Terminal 1: PostgreSQL & Redis
brew services start postgresql
brew services start redis

# Terminal 2: Backend
cd backend
alembic upgrade head
uvicorn app.main:app --reload

# Terminal 3: Frontend
cd frontend
npm run dev

# Open browser
open http://localhost:3000
```

### 11.2 Required System Tools

```bash
# macOS
brew install python@3.11 postgresql@15 redis node@18

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 postgresql-15 redis-server nodejs npm

# Windows (using Chocolatey)
choco install python postgresql redis nodejs
```

---

## 12. Glossary

| Term | Definition |
|------|------------|
| **MCP Server** | Model Context Protocol server - provides tools for external services |
| **LangGraph** | Framework for building stateful multi-agent applications |
| **OpenRouter** | Unified API gateway for multiple LLM providers |
| **SSE** | Server-Sent Events - streaming protocol for one-way communication |
| **Clerk** | Authentication and user management platform |
| **Pydantic** | Data validation library for Python |
| **SQLAlchemy** | SQL toolkit and ORM for Python |
| **Zustand** | Small, fast state management for React |

---

This technology stack document serves as the single source of truth for all technical decisions in the Personal AI Agent project. All team members should refer to this document when making technology-related decisions or when onboarding new developers.