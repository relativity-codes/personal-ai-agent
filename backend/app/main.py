from contextlib import asynccontextmanager
import asyncio
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.api.middleware import AuthMiddleware
from app.api.routers.v1 import agents, chat, mcp, mcp_oauth, webhooks, user_router, audit_log_router, chat_history_router, plan_router, task_router, session_router, auth, mcp_credential_router
from app.api.websocket import chat as ws_chat
from app.config import settings
from app.core.openrouter import OpenRouterClient
from app.db.session import close_db, init_db
from app.services.cache_service import redis_client
from app.mcp_alt.registry import mcp_alt_registry as mcp_registry_service
# from app.services.mcp_registry import mcp_registry

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)

_startup_lock = asyncio.Lock()
_startup_complete = False


async def _application_startup(app: FastAPI) -> None:
    await init_db()
    await redis_client.connect()
    app.state.openrouter = OpenRouterClient(
        api_key=settings.OPENROUTER_API_KEY or None,
        base_url=settings.OPENROUTER_BASE_URL,
    )
    await mcp_registry_service.initialize()
    logger.info("startup complete")


async def _application_shutdown() -> None:
    await close_db()
    await redis_client.disconnect()
    logger.info("shutdown complete")


async def ensure_application_started(app: FastAPI) -> None:
    """Idempotent startup for ASGI servers that run lifespan (uvicorn) and those that do not (Zappa ASGI)."""
    global _startup_complete
    if _startup_complete:
        return
    async with _startup_lock:
        if _startup_complete:
            return
        await _application_startup(app)
        _startup_complete = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _startup_complete
    await ensure_application_started(app)
    yield
    await _application_shutdown()
    _startup_complete = False


class _EnsureStartupMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        await ensure_application_started(request.app)
        return await call_next(request)


app = FastAPI(
    title="Personal AI Agent API",
    version="3.0.0",
    description="Multi-agent personal AI system",
    lifespan=lifespan,
)

app.add_middleware(AuthMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)
app.add_middleware(_EnsureStartupMiddleware)

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(mcp_oauth.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(user_router.router, prefix="/api/v1/users", tags=["users"])
app.include_router(audit_log_router.router, prefix="/api/v1/audit-logs", tags=["audit-logs"])
app.include_router(chat_history_router.router, prefix="/api/v1/chat-history", tags=["chat-history"])
app.include_router(plan_router.router, prefix="/api/v1/plans", tags=["plans"])
app.include_router(task_router.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(session_router.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(mcp_credential_router.router, prefix="/api/v1/mcp-credentials", tags=["mcp"])
app.include_router(ws_chat.router, prefix="/ws", tags=["websocket"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])


@app.get("/health")
async def health_check():
    from app.db.session import db_health
    from app.services.cache_service import redis_client as rc

    return {
        "status": "healthy",
        "version": "3.0.0",
        "services": {
            "database": await db_health(),
            "redis": await rc.health(),
            "mcp": await mcp_registry_service.summary(),
        },
    }

# -------------------------
# Static Frontend Serving
# -------------------------

@app.get("/{full_path:path}", tags=["Frontend"])
async def serve_frontend(full_path: str):
    """
    Serves the static frontend assets.

    This catch-all route handles serving files for the Next.js frontend.
    - If the requested path matches a file in the 'static' directory (e.g., an image or a JS chunk), it serves that file.
    - Otherwise, it serves the 'index.html' file, allowing the client-side router to handle the URL.
    """
    # Construct the path to the file in the static directory
    # The path should be relative to the 'backend' directory where the app runs
    static_file_path = os.path.join("static", full_path)
    
    # 1. If it's a file that exists, serve it (e.g., /_next/static/...)
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    
    # 2. If it's a directory, check for index.html within it (for trailingSlash: true)
    if os.path.isdir(static_file_path):
        dir_index = os.path.join(static_file_path, "index.html")
        if os.path.isfile(dir_index):
            return FileResponse(dir_index)

    # 3. Otherwise, serve root index.html for SPA routing
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"message": "Personal AI Agent API is running. Frontend static files not found."}
