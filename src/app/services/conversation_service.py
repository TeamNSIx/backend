from uuid import UUID

from src.app.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)
from src.app.repositories.conversation_repository import ConversationRepository


class ConversationService:
    def __init__(self, repository: ConversationRepository) -> None:
        self.repository = repository

    async def list_conversations(self, user_id: UUID | None = None) -> list[ConversationPublic]:
        if user_id is None:
            conversations = await self.repository.get_all()
        else:
            conversations = await self.repository.list_by_user(user_id)
        return [ConversationPublic.model_validate(item) for item in conversations]

    async def get_conversation(self, conversation_id: UUID) -> ConversationPublic | None:
        conversation = await self.repository.get_by_id(conversation_id)
        if conversation is None:
            return None
        return ConversationPublic.model_validate(conversation)

    async def create_conversation(self, payload: ConversationCreate) -> ConversationPublic:
        conversation = Conversation.model_validate(payload)
        created = await self.repository.add(conversation)
        return ConversationPublic.model_validate(created)

    async def update_conversation(
        self,
        conversation_id: UUID,
        payload: ConversationUpdate,
    ) -> ConversationPublic | None:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(conversation_id, updates)
        if updated is None:
            return None
        return ConversationPublic.model_validate(updated)
