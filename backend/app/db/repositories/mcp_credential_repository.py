from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.mcp_credential import MCPCredential

class MCPCredentialRepository:
    @staticmethod
    async def get_by_id(db: AsyncSession, credential_id: UUID) -> Optional[MCPCredential]:
        result = await db.execute(select(MCPCredential).where(MCPCredential.id == credential_id))
        return result.scalars().first()

    @staticmethod
    async def get_by_user(db: AsyncSession, user_id: UUID) -> List[MCPCredential]:
        result = await db.execute(select(MCPCredential).where(MCPCredential.user_id == user_id))
        return list(result.scalars().all())

    @staticmethod
    async def get_by_user_and_server(db: AsyncSession, user_id: UUID, server_id: str) -> Optional[MCPCredential]:
        result = await db.execute(
            select(MCPCredential).where(
                MCPCredential.user_id == user_id, 
                MCPCredential.server_id == server_id
            )
        )
        return result.scalars().first()

    @staticmethod
    async def create(db: AsyncSession, user_id: UUID, server_id: str, credentials: dict) -> MCPCredential:
        db_credential = MCPCredential(
            user_id=user_id,
            server_id=server_id,
            credentials=credentials
        )
        db.add(db_credential)
        await db.flush()
        return db_credential

    @staticmethod
    async def update(db: AsyncSession, credential_id: UUID, credentials: dict) -> Optional[MCPCredential]:
        db_credential = await MCPCredentialRepository.get_by_id(db, credential_id)
        if db_credential:
            db_credential.credentials = credentials
            await db.flush()
        return db_credential

    @staticmethod
    async def delete(db: AsyncSession, credential_id: UUID) -> bool:
        db_credential = await MCPCredentialRepository.get_by_id(db, credential_id)
        if db_credential:
            await db.delete(db_credential)
            await db.flush()
            return True
        return False
