from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.db.database import get_session
from src.app.models.message import Message
from src.app.repositories.base import BaseRepository


class MessageRepository(BaseRepository[Message]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=Message)

    async def list_by_conversation(self, conversation_id: UUID) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_by_conversation_page(
        self,
        conversation_id: UUID,
        offset: int,
        limit: int,
    ) -> list[Message]:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at, Message.id)
            .offset(offset)
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def count_by_conversation(self, conversation_id: UUID) -> int:
        return await self.count(conversation_id=conversation_id)
