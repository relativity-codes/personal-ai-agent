import asyncio
from uuid import UUID
from app.db.database import get_db
from app.db.repositories.mcp_credential_repository import MCPCredentialRepository
from app.api.schemas import MCPServiceId

async def check_creds():
    user_id = UUID('b4282c03-1205-4ae8-80ba-a5ea53cbe459')
    async for db in get_db():
        creds = await MCPCredentialRepository.get_by_user_and_server(db, user_id, MCPServiceId.NOTION)
        if creds:
            print(f"Notion credentials found for user")
        else:
            print("No Notion credentials found")
        break

if __name__ == "__main__":
    asyncio.run(check_creds())
