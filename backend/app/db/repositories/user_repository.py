from app.db.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class UserRepository:
    @staticmethod
    async def get_by_clerk_id(session: AsyncSession, clerk_id: str):
        result = await session.execute(select(User).where(User.clerk_id == clerk_id))
        return result.scalars().first()

    @staticmethod
    async def create(session: AsyncSession, **kwargs):
        user = User(**kwargs)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user
