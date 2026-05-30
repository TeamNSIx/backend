from typing import Annotated
from uuid import UUID

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Query,
    Request,
    Security,
    status,
)
from pydantic import BaseModel, Field

from src.app.core.responses import (
    auth_responses,
    common_responses,
    detail_responses,
    merge_responses,
)
from src.app.dependencies import (
    ConversationServiceDep,
    FeedbackServiceDep,
    MessageServiceDep,
)
from src.app.dependencies.auth import get_current_user
from src.app.dependencies.pagination import PaginationDep
from src.app.models.conversation import (
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)
from src.app.models.feedback import FeedbackCreate, FeedbackPublic
from src.app.models.message import MessagePublic
from src.app.models.user import UserPublic
from src.app.schemas.pagination import PaginatedResponse
from src.utils.error import ForbiddenError

router = APIRouter(prefix='/conversations', tags=['conversations'])

_responses = merge_responses(common_responses, auth_responses, detail_responses)

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
    conversation: ConversationPublic,
    current_user: UserPublic,
) -> ConversationPublic:
    if conversation.user_id != current_user.id:
        raise ForbiddenError()
    return conversation


async def get_accessible_conversation(
    conversation_id: UUID,
    current_user: ConversationDetailAuth,
    conversation_service: ConversationServiceDep,
) -> ConversationPublic:
    conversation = await conversation_service.get_conversation(conversation_id)
    return _ensure_conversation_access(conversation, current_user)


async def get_accessible_conversation_for_update(
    conversation_id: UUID,
    current_user: ConversationUpdateAuth,
    conversation_service: ConversationServiceDep,
) -> ConversationPublic:
    conversation = await conversation_service.get_conversation(conversation_id)
    return _ensure_conversation_access(conversation, current_user)


ConversationAccessDep = Annotated[
    ConversationPublic,
    Depends(get_accessible_conversation),
]
ConversationUpdateAccessDep = Annotated[
    ConversationPublic,
    Depends(get_accessible_conversation_for_update),
]


@router.get(
    '/',
    response_model=PaginatedResponse[ConversationPublic],
    responses=_responses,
)
async def list_conversations(
    request: Request,  # noqa: ARG001
    current_user: ConversationListAuth,
    service: ConversationServiceDep,
    pagination: PaginationDep,
    user_id: OptionalUserIdQuery = None,
):
    if user_id is not None and user_id != current_user.id:
        raise ForbiddenError()
    user_id = current_user.id if user_id is None else user_id
    return await service.list_conversations(pagination, user_id=user_id)


@router.get(
    '/{conversation_id}/messages',
    response_model=PaginatedResponse[MessagePublic],
    responses=_responses,
)
async def list_messages(
    request: Request,  # noqa: ARG001
    conversation_id: UUID,
    conversation: ConversationAccessDep,
    message_service: MessageServiceDep,
    pagination: PaginationDep,
):
    _ = conversation_id
    return await message_service.list_messages(conversation.id, pagination)


@router.post(
    '/{conversation_id}/messages',
    response_model=ChatMessageResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_responses,
)
async def create_message(
    conversation_id: UUID,
    conversation: ConversationUpdateAccessDep,
    payload: ChatMessageCreate,
    message_service: MessageServiceDep,
    background_tasks: BackgroundTasks,
):
    _ = conversation_id
    user_message, bot_message = await message_service.create_chat_pair(
        conversation_id=conversation.id,
        user_text=payload.content,
        background_tasks=background_tasks,
    )
    return ChatMessageResponse(
        user_message=user_message,
        bot_message=bot_message,
    )


@router.get(
    '/{conversation_id}/feedback',
    response_model=PaginatedResponse[FeedbackPublic],
    responses=_responses,
)
async def list_feedback(
    request: Request,  # noqa: ARG001
    conversation_id: UUID,
    conversation: ConversationAccessDep,
    feedback_service: FeedbackServiceDep,
    pagination: PaginationDep,
):
    _ = conversation_id
    return await feedback_service.list_feedback(conversation.id, pagination)


@router.post(
    '/{conversation_id}/feedback',
    response_model=FeedbackPublic,
    status_code=status.HTTP_201_CREATED,
    responses=_responses,
)
async def create_feedback(
    conversation_id: UUID,
    conversation: ConversationUpdateAccessDep,
    payload: ConversationFeedbackCreate,
    feedback_service: FeedbackServiceDep,
):
    _ = conversation_id
    return await feedback_service.create_feedback(
        FeedbackCreate(
            conversation_id=conversation.id,
            rating=payload.rating,
            comment=payload.comment,
        ),
    )


@router.get(
    '/{conversation_id}',
    response_model=ConversationPublic,
    responses=_responses,
)
async def get_conversation(
    conversation_id: UUID,
    conversation: ConversationAccessDep,
):
    _ = conversation_id
    return conversation


@router.post(
    '/',
    response_model=ConversationPublic,
    status_code=status.HTTP_201_CREATED,
    responses=_responses,
)
async def create_conversation(
    payload: ConversationCreate,
    current_user: ConversationCreateAuth,
    service: ConversationServiceDep,
):
    if payload.user_id != current_user.id:
        raise ForbiddenError()
    return await service.create_conversation(payload)


@router.patch(
    '/{conversation_id}',
    response_model=ConversationPublic,
    responses=_responses,
)
async def update_conversation(
    conversation_id: UUID,
    conversation: ConversationUpdateAccessDep,
    payload: ConversationUpdate,
    service: ConversationServiceDep,
):
    _ = conversation_id
    return await service.update_conversation(conversation.id, payload)
