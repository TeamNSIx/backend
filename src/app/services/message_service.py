from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.app.models.message import (
    Message,
    MessageCreate,
    MessagePublic,
    MessageSender,
)
from src.app.repositories.message_repository import MessageRepository
from src.app.services.llm_service import LLMService


class MessageService:
    def __init__(
        self,
        repository: Annotated[MessageRepository, Depends(MessageRepository)],
        llm_service: Annotated[LLMService, Depends(LLMService)],
    ) -> None:
        self.repository = repository
        self.llm_service = llm_service

    async def list_messages(self, conversation_id: UUID) -> list[MessagePublic]:
        messages = await self.repository.list_by_conversation(conversation_id)
        return [MessagePublic.model_validate(message) for message in messages]

    async def create_message(self, payload: MessageCreate) -> MessagePublic:
        message = Message.model_validate(payload)
        created = await self.repository.add(message)
        return MessagePublic.model_validate(created)

    async def create_chat_pair(
        self,
        conversation_id: UUID,
        user_text: str,
    ) -> tuple[MessagePublic, MessagePublic]:
        user_message = await self.create_message(
            MessageCreate(
                conversation_id=conversation_id,
                sender=MessageSender.USER,
                content=user_text,
            ),
        )
        answer, metadata = await self.llm_service.generate_answer(user_text)
        bot_message = await self.create_message(
            MessageCreate(
                conversation_id=conversation_id,
                sender=MessageSender.SYSTEM,
                content=answer,
                message_metadata=metadata,
            ),
        )
        return user_message, bot_message
