from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.models.conversation import Conversation
from src.app.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[Conversation]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Conversation)

    async def list_by_user(self, user_id: UUID) -> list[Conversation]:
        statement = select(Conversation).where(Conversation.user_id == user_id)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def update_fields(
        self,
        entity_id: UUID,
        updates: dict,
    ) -> Conversation | None:
        conversation = await self.get_by_id(entity_id)
        if conversation is None:
            return None

        for key, value in updates.items():
            setattr(conversation, key, value)

        await self.session.commit()
        await self.session.refresh(conversation)
        return conversation
