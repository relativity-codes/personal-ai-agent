from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import agents, chat, mcp, mcp_oauth, webhooks
from app.api.websocket import chat as ws_chat
from app.config import settings
from app.core.openrouter import OpenRouterClient
from app.db.session import close_db, init_db
from app.services.cache_service import redis_client
from app.mcp.registry import mcp_registry as mcp_registry_service

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await redis_client.connect()
    app.state.openrouter = OpenRouterClient(
        api_key=settings.OPENROUTER_API_KEY or None,
        base_url=settings.OPENROUTER_BASE_URL,
    )
    await mcp_registry_service.initialize()
    logger.info("startup complete")
    yield
    await close_db()
    await redis_client.disconnect()
    logger.info("shutdown complete")


app = FastAPI(
    title="Personal AI Agent API",
    version="3.0.0",
    description="Multi-agent personal AI system",
    lifespan=lifespan,
)

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
app.include_router(ws_chat.router, prefix="/ws", tags=["websocket"])


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
            "mcp": mcp_registry_service.summary(),
        },
    }
