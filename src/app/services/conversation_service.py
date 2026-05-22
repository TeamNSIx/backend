from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.app.models.conversation import (
    Conversation,
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)
from src.app.repositories.conversation_repository import ConversationRepository
from src.app.schemas.pagination import PaginatedResponse, PaginationParams
from src.utils.error import NotFoundError


class ConversationService:
    def __init__(
        self,
        repository: Annotated[ConversationRepository, Depends(ConversationRepository)],
    ) -> None:
        self.repository = repository

    async def list_conversations(
        self,
        pagination: PaginationParams,
        user_id: UUID | None = None,
    ) -> PaginatedResponse[ConversationPublic]:
        filters = {'user_id': user_id} if user_id is not None else {}
        total = await self.repository.count(**filters)
        conversations = await self.repository.get_page(
            pagination.offset,
            pagination.page_size,
            **filters,
        )
        items = [ConversationPublic.model_validate(item) for item in conversations]
        return PaginatedResponse.build(items, total, pagination)

    async def get_conversation(self, conversation_id: UUID) -> ConversationPublic:
        conversation = await self.repository.get_by_id(conversation_id)
        if conversation is None:
            raise NotFoundError(detail='Conversation not found')
        return ConversationPublic.model_validate(conversation)

    async def create_conversation(
        self, payload: ConversationCreate
    ) -> ConversationPublic:
        conversation = Conversation.model_validate(payload)
        created = await self.repository.add(conversation)
        return ConversationPublic.model_validate(created)

    async def update_conversation(
        self,
        conversation_id: UUID,
        payload: ConversationUpdate,
    ) -> ConversationPublic:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(conversation_id, updates)
        if updated is None:
            raise NotFoundError(detail='Conversation not found')
        return ConversationPublic.model_validate(updated)
