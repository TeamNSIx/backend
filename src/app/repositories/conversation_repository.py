from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.conversation import Conversation
from src.app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Conversation)

    async def list_by_user(self, user_id: UUID) -> list[Conversation]:
        return await self.get_all(user_id=user_id)
