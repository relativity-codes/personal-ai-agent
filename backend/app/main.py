from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import FileResponse
from app.api.middleware import AuthMiddleware
from app.api.routers.v1 import agents, chat, mcp, mcp_oauth, webhooks, user_router, audit_log_router, chat_history_router, plan_router, session_router, auth, mcp_credential_router
from app.api.websocket import chat as ws_chat
from app.config import settings
from app.core.openrouter import OpenRouterClient
from app.db.session import close_db, init_db

from app.mcp_alt.registry import mcp_alt_registry as mcp_registry_service


logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    app.state.openrouter = OpenRouterClient(
        api_key=settings.OPENROUTER_API_KEY or None,
        base_url=settings.OPENROUTER_BASE_URL,
    )
    await mcp_registry_service.initialize()

    logger.info("startup complete")
    yield
    await close_db()

    logger.info("shutdown complete")


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

app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(mcp.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(mcp_oauth.router, prefix="/api/v1/mcp", tags=["mcp"])
app.include_router(webhooks.router, prefix="/api/v1/webhooks", tags=["webhooks"])
app.include_router(user_router.router, prefix="/api/v1/users", tags=["users"])
app.include_router(audit_log_router.router, prefix="/api/v1/audit-logs", tags=["audit-logs"])
app.include_router(chat_history_router.router, prefix="/api/v1/chat-history", tags=["chat-history"])
app.include_router(plan_router.router, prefix="/api/v1/plans", tags=["plans"])

app.include_router(session_router.router, prefix="/api/v1/sessions", tags=["sessions"])
app.include_router(mcp_credential_router.router, prefix="/api/v1/mcp-credentials", tags=["mcp"])
app.include_router(ws_chat.router, prefix="/ws", tags=["websocket"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])


@app.get("/health")
async def health_check():
    from app.db.session import db_health


    return {
        "status": "healthy",
        "version": "3.0.0",
        "services": {
            "database": await db_health(),

            "mcp": await mcp_registry_service.summary(),
        },
    }

# Static Frontend Serving
@app.get("/{full_path:path}", tags=["Frontend"])
async def serve_frontend(full_path: str):
    """Serves the static frontend assets or falls back to index.html for SPA routing."""
    static_file_path = os.path.join("static", full_path)
    
    if os.path.isfile(static_file_path):
        return FileResponse(static_file_path)
    
    if os.path.isdir(static_file_path):
        dir_index = os.path.join(static_file_path, "index.html")
        if os.path.isfile(dir_index):
            return FileResponse(dir_index)

    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {"message": "API is running. Frontend assets not found."}
