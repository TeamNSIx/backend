from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends

from src.app.models.message import (
    Message,
    MessageCreate,
    MessagePublic,
    MessageSender,
)
from src.app.repositories.message_repository import MessageRepository
from src.app.schemas.pagination import PaginatedResponse, PaginationParams
from src.app.services.rag_service import RAGService


class MessageService:
    def __init__(
        self,
        repository: Annotated[MessageRepository, Depends(MessageRepository)],
        rag_service: Annotated[RAGService, Depends(RAGService)],
    ) -> None:
        self.repository = repository
        self.rag_service = rag_service

    async def list_messages(
        self,
        conversation_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse[MessagePublic]:
        total = await self.repository.count_by_conversation(conversation_id)
        messages = await self.repository.list_by_conversation_page(
            conversation_id,
            pagination.offset,
            pagination.page_size,
        )
        items = [MessagePublic.model_validate(message) for message in messages]
        return PaginatedResponse.build(items, total, pagination)

    async def create_message(self, payload: MessageCreate) -> MessagePublic:
        message = Message.model_validate(payload)
        created = await self.repository.add(message)
        return MessagePublic.model_validate(created)

    async def create_chat_pair(
        self,
        conversation_id: UUID,
        user_text: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> tuple[MessagePublic, MessagePublic]:
        user_message = await self.create_message(
            MessageCreate(
                conversation_id=conversation_id,
                sender=MessageSender.USER,
                content=user_text,
            ),
        )
        bot_text, metadata = await self.rag_service.generate_answer(
            user_text,
            background_tasks,
        )
        bot_message = await self.create_message(
            MessageCreate(
                conversation_id=conversation_id,
                sender=MessageSender.SYSTEM,
                content=bot_text,
                message_metadata=metadata,
            ),
        )
        return user_message, bot_message
