import asyncio
from uuid import UUID
from app.db.database import get_db
from app.db.repositories.user_repository import UserRepository

async def check_user():
    user_id = UUID('b4282c03-1205-4ae8-80ba-a5ea53cbe459')
    async for db in get_db():
        user = await UserRepository.get_by_id(db, user_id)
        if user:
            print(f"User Name: {user.name}")
            print(f"Default Notion DB: {user.default_notion_db}")
            print(f"Default GitHub Repo: {user.default_github_repo}")
        else:
            print("User not found")
        break

if __name__ == "__main__":
    asyncio.run(check_user())
