
from typing import List, Dict
from sqlalchemy import select, desc, insert, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models.chat_history import ChatHistory
from uuid import UUID

class ChatHistoryRepository:
    """
    Repository for managing chat history in the database.
    """

    @staticmethod
    async def get_history(session: AsyncSession, session_id: str) -> List[Dict]:
        """
        Get the last 4 chat history messages for a given session ID.
        """
        # Create a subquery to select the last 4 messages for the session
        if (session_id is None):
            return []
        
        subquery = (
            select(ChatHistory)
            .where(ChatHistory.session_id == session_id)
            .order_by(desc(ChatHistory.timestamp))
            .limit(10)
            .alias("latest_messages")
        )

        # Create the main query to order the subquery results in ascending order
        query = select(subquery).order_by(subquery.c.timestamp)

        results = await session.execute(query)
        # Convert the result to a list of dictionaries to match the expected output type
        return [dict(row) for row in results.mappings().all()]

    @staticmethod
    async def add_message(session: AsyncSession, session_id: str, role: str, message: str):
        """
        Add a message to the chat history.
        """
        chat_history = ChatHistory(session_id=session_id, role=role, message=message)
        session.add(chat_history)
        await session.commit()
        await session.refresh(chat_history)
        return chat_history

    @staticmethod
    async def get_all_for_user(session: AsyncSession, user_id: UUID, skip: int = 0, limit: int = 100):
        from app.db.models.session import Session
        from sqlalchemy import cast, String
        
        query = (
            select(ChatHistory)
            .join(Session, cast(Session.id, String) == ChatHistory.session_id)
            .where(Session.user_id == user_id)
            .order_by(ChatHistory.timestamp.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_all(session: AsyncSession, skip: int = 0, limit: int = 100):
        result = await session.execute(select(ChatHistory).order_by(ChatHistory.timestamp.desc()).offset(skip).limit(limit))
        return result.scalars().all()

    @staticmethod
    async def get_by_id(session: AsyncSession, history_id: UUID):
        result = await session.execute(select(ChatHistory).where(ChatHistory.id == history_id))
        return result.scalars().first()

    @staticmethod
    async def delete_by_id(session: AsyncSession, history_id: UUID) -> bool:
        result = await session.execute(delete(ChatHistory).where(ChatHistory.id == history_id))
        await session.commit()
        return result.rowcount > 0
