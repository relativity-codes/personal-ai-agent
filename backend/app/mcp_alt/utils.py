from uuid import UUID
from typing import Optional, Dict, Any
from app.db.database import get_db
from app.db.repositories.mcp_credential_repository import MCPCredentialRepository
from app.api.schemas import MCPServiceId
import contextlib

@contextlib.asynccontextmanager
async def get_db_session():
    async for db in get_db():
        yield db

async def get_mcp_credentials(user_id: str, server_id: MCPServiceId) -> Dict[str, Any]:
    """Fetch credentials for a specific user and server from the database."""
    try:
        uid = UUID(user_id)
        async with get_db_session() as db:
            creds = await MCPCredentialRepository.get_by_user_and_server(db, uid, server_id)
            return creds.credentials if creds else {}
    except Exception:
        return {}

async def save_mcp_credentials(user_id: str, server_id: MCPServiceId, credentials: Dict[str, Any]) -> None:
    """Save or update credentials for a specific user and server in the database."""
    try:
        uid = UUID(user_id)
        async with get_db_session() as db:
            existing = await MCPCredentialRepository.get_by_user_and_server(db, uid, server_id)
            if existing:
                await MCPCredentialRepository.update(db, existing.id, credentials)
            else:
                await MCPCredentialRepository.create(db, uid, server_id, credentials)
            await db.commit()
    except Exception as e:
        import logging
        logging.getLogger("mcp-utils").error(f"Failed to save credentials: {e}")
