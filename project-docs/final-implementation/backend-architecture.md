# Backend Architecture

## Summary

The backend is a FastAPI application that provides the authenticated API, agent orchestration entrypoints, integration discovery/invocation endpoints, persistence, caching, and production static-file serving.

## Backend Folder Structure

```text
backend/
├── app/
│   ├── main.py               # FastAPI app entrypoint
│   ├── config.py             # Environment configuration
│   ├── api/
│   │   ├── middleware.py     # Cookie/JWT auth middleware
│   │   ├── deps.py           # Auth/session dependencies
│   │   └── routers/
│   │       └── v1/           # Versioned REST routes
│   ├── agents/               # LangGraph workflow nodes
│   ├── db/
│   │   ├── models/           # SQLAlchemy models
│   │   ├── repositories/     # Data access layer
│   │   └── session.py        # Async DB engine/session
│   ├── mcp_alt/              # Runtime integration servers
│   ├── services/             # Redis cache and services
│   └── core/                 # OpenRouter client and prompts
└── alembic/                  # Migration versions and env
```

## Application Startup

`app.main` creates the FastAPI app and registers:

- `AuthMiddleware` for authenticated `/api/*` access.
- CORS middleware using `settings.cors_origins_list`.
- `TrustedHostMiddleware` using `settings.allowed_hosts_list`.
- REST routers under `/api/v1`.
- WebSocket chat under `/ws`.
- `GET /health`.
- A catch-all route that serves `static/` files and falls back to `static/index.html`.

The app lifespan initializes the database schema, Redis connection, OpenRouter client, and runtime MCP registry:

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await redis_client.connect()
    app.state.openrouter = OpenRouterClient(...)
    await mcp_registry_service.initialize()
    yield
    await close_db()
    await redis_client.disconnect()
```

## Configuration

Configuration lives in [`../../backend/app/config.py`](../../backend/app/config.py). It uses `pydantic-settings` plus `python-decouple` to read environment variables.

Important runtime groups:

- App/auth: `APP_ENV`, `DEBUG`, `SECRET_KEY`, `ALGORITHM`, `SECURE_COOKIES`.
- Deployment safety: `CORS_ORIGINS`, `ALLOWED_HOSTS`, `HOST`.
- Database: direct `DATABASE_URL` or Postgres-compatible `POSTGRES_*` values.
- Cache: direct `REDIS_URL` or Redis component values.
- LLM: `OPENROUTER_API_KEY`, `OPENROUTER_BASE_URL`, model names.
- Integrations: Google, GitHub, Notion, Gmail credentials and OAuth client values.
- Limits: rate limit, task timeout, and maximum execution iterations.

The current deployment target uses CockroachDB through the Postgres-compatible SQLAlchemy URL and Redis Cloud through `REDIS_URL`.

## Authentication

The current authentication model is Google sign-in plus an application JWT.

1. The frontend obtains a Google credential.
2. `POST /api/v1/auth/google` verifies the Google ID token using `google-auth`.
3. `UserService.get_or_create_user_from_google` creates or loads the application user.
4. `create_access_token` signs an application JWT with the internal user UUID as `sub`.
5. `set_access_cookies` stores the token in the `access_token` httpOnly cookie.

Protected API requests pass through [`../../backend/app/api/middleware.py`](../../backend/app/api/middleware.py). The middleware allows public paths such as auth, health, docs, and static assets, then validates the cookie for `/api/*` routes.

Route dependencies in [`../../backend/app/api/deps.py`](../../backend/app/api/deps.py) also decode the same JWT and load the user from the database. The chat endpoint uses this dependency to build agent state with the current user's ID and profile context.

## API Surface

The routers are mounted in [`../../backend/app/main.py`](../../backend/app/main.py):

- `/api/v1/auth/google`, `/api/v1/auth/logout`, `/api/v1/users/me`: authentication and current user.
- `/api/v1/chat`: REST chat endpoint that invokes the agent graph.
- `/api/v1/agents`: agent/plan status surface.
- `/api/v1/mcp`: integration server discovery, tool listing, invocation, and OAuth routes.
- `/api/v1/users`: user profile routes.
- `/api/v1/sessions`: chat sessions.
- `/api/v1/chat-history`: persisted conversation history.
- `/api/v1/plans`: execution plans.
- `/api/v1/tasks`: task records/status.
- `/api/v1/audit-logs`: audit log access.
- `/api/v1/mcp-credentials`: user integration credentials.
- `/ws/chat`: WebSocket chat route.

## Chat Request Flow

The REST chat endpoint is implemented in [`../../backend/app/api/routers/v1/chat.py`](../../backend/app/api/routers/v1/chat.py).

For each request it:

1. Authenticates the user through `get_current_user`.
2. Creates a new session or verifies the supplied `session_id`.
3. Loads chat history for the session.
4. Loads user profile context such as name, email, timezone, default GitHub repo, and default Notion database.
5. Builds `AgentState`.
6. Invokes `create_managerial_graph().ainvoke(initial_state)`.
7. Persists the user message and final agent response.
8. Returns `{ response, session_id }`.

## Persistence

The backend uses async SQLAlchemy with repositories to keep route and agent code away from raw queries.

Core models are registered in [`../../backend/app/db/models/__init__.py`](../../backend/app/db/models/__init__.py):

- `User`
- `Session`
- `ChatHistory`
- `ExecutionPlan`
- `Task`
- `AuditLog`
- `MCPCredential`

Repository implementations live in [`../../backend/app/db/repositories`](../../backend/app/db/repositories). Alembic migrations live in [`../../backend/alembic`](../../backend/alembic).

## Cache and Health Checks

Redis is wrapped by [`../../backend/app/services/cache_service.py`](../../backend/app/services/cache_service.py). It is used for JSON cache operations and agent plan/task state updates.

`GET /health` reports:

- Backend status and version.
- Database health.
- Redis health.
- MCP registry summary.

## Static Frontend Serving

The backend catch-all route serves the exported Next.js app from the `static/` directory. During Cloud Run image build, the root Dockerfile copies `frontend/out` into `/app/static`. This is what allows the production deployment to run as a single Cloud Run service.

