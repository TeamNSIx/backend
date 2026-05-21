from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Security, status
from pydantic import BaseModel, Field

from src.app.dependencies import (
    ConversationServiceDep,
    FeedbackServiceDep,
    MessageServiceDep,
)
from src.app.dependencies.auth import get_current_user
from src.app.models.conversation import (
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)
from src.app.models.feedback import FeedbackCreate, FeedbackPublic
from src.app.models.message import MessagePublic
from src.app.models.user import UserPublic

router = APIRouter(prefix='/conversations', tags=['conversations'])

ConversationListAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['conversation:list']),
]
ConversationDetailAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['conversation:detail']),
]
ConversationCreateAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['conversation:create']),
]
ConversationUpdateAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['conversation:update']),
]

OptionalUserIdQuery = Annotated[UUID | None, Query()]


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)


class ChatMessageResponse(BaseModel):
    user_message: MessagePublic
    bot_message: MessagePublic


class ConversationFeedbackCreate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


def _ensure_conversation_access(
    conversation: ConversationPublic | None,
    current_user: UserPublic,
) -> ConversationPublic:
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversation not found',
        )
    if conversation.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden',
        )
    return conversation


@router.get('/', response_model=list[ConversationPublic])
async def list_conversations(
    current_user: ConversationListAuth,
    service: ConversationServiceDep,
    user_id: OptionalUserIdQuery = None,
):
    if user_id is not None and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden',
        )
    user_id = current_user.id if user_id is None else user_id
    return await service.list_conversations(user_id=user_id)


@router.get('/{conversation_id}/messages', response_model=list[MessagePublic])
async def list_messages(
    conversation_id: UUID,
    current_user: ConversationDetailAuth,
    conversation_service: ConversationServiceDep,
    message_service: MessageServiceDep,
):
    conversation = await conversation_service.get_conversation(conversation_id)
    _ensure_conversation_access(conversation, current_user)
    return await message_service.list_messages(conversation_id)


@router.post(
    '/{conversation_id}/messages',
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_message(
    conversation_id: UUID,
    payload: ChatMessageCreate,
    current_user: ConversationUpdateAuth,
    conversation_service: ConversationServiceDep,
    message_service: MessageServiceDep,
):
    conversation = await conversation_service.get_conversation(conversation_id)
    _ensure_conversation_access(conversation, current_user)
    user_message, bot_message = await message_service.create_chat_pair(
        conversation_id=conversation_id,
        user_text=payload.content,
    )
    return ChatMessageResponse(
        user_message=user_message,
        bot_message=bot_message,
    )


@router.get('/{conversation_id}/feedback', response_model=list[FeedbackPublic])
async def list_feedback(
    conversation_id: UUID,
    current_user: ConversationDetailAuth,
    conversation_service: ConversationServiceDep,
    feedback_service: FeedbackServiceDep,
):
    conversation = await conversation_service.get_conversation(conversation_id)
    _ensure_conversation_access(conversation, current_user)
    return await feedback_service.list_feedback(conversation_id)


@router.post(
    '/{conversation_id}/feedback',
    response_model=FeedbackPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_feedback(
    conversation_id: UUID,
    payload: ConversationFeedbackCreate,
    current_user: ConversationUpdateAuth,
    conversation_service: ConversationServiceDep,
    feedback_service: FeedbackServiceDep,
):
    conversation = await conversation_service.get_conversation(conversation_id)
    _ensure_conversation_access(conversation, current_user)
    return await feedback_service.create_feedback(
        FeedbackCreate(
            conversation_id=conversation_id,
            rating=payload.rating,
            comment=payload.comment,
        ),
    )


@router.get('/{conversation_id}', response_model=ConversationPublic)
async def get_conversation(
    conversation_id: UUID,
    current_user: ConversationDetailAuth,
    service: ConversationServiceDep,
):
    conversation = await service.get_conversation(conversation_id)
    return _ensure_conversation_access(conversation, current_user)


@router.post(
    '/',
    response_model=ConversationPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreate,
    current_user: ConversationCreateAuth,
    service: ConversationServiceDep,
):
    if payload.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Forbidden',
        )
    return await service.create_conversation(payload)


@router.patch('/{conversation_id}', response_model=ConversationPublic)
async def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    current_user: ConversationUpdateAuth,
    service: ConversationServiceDep,
):
    existing = await service.get_conversation(conversation_id)
    _ensure_conversation_access(existing, current_user)
    conversation = await service.update_conversation(conversation_id, payload)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversation not found',
        )
    return conversation
