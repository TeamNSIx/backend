from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import get_session
from src.app.models.feedback import Feedback
from src.app.repositories.base import BaseRepository


class FeedbackRepository(BaseRepository[Feedback]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=Feedback)

    async def list_by_conversation(self, conversation_id: UUID) -> list[Feedback]:
        return await self.get_all(conversation_id=conversation_id)
