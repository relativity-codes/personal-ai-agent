import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.core.openrouter import OpenRouterClient
from app.db.session import close_db, init_db
from app.main import app
from app.mcp_alt.registry import mcp_alt_registry as mcp_registry


@pytest_asyncio.fixture
async def client():
    await init_db()
    app.state.openrouter = OpenRouterClient(
        api_key=settings.OPENROUTER_API_KEY or None,
        base_url=settings.OPENROUTER_BASE_URL,
    )
    await mcp_registry.initialize()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    await close_db()
