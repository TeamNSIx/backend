from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, Security, status

from src.app.dependencies import ConversationServiceDep
from src.app.dependencies.auth import get_current_user
from src.app.models.conversation import (
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)
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


@router.get('/', response_model=list[ConversationPublic])
async def list_conversations(
    _: ConversationListAuth,
    service: ConversationServiceDep,
    user_id: OptionalUserIdQuery = None,
):
    return await service.list_conversations(user_id=user_id)


@router.get('/{conversation_id}', response_model=ConversationPublic)
async def get_conversation(
    conversation_id: UUID,
    _: ConversationDetailAuth,
    service: ConversationServiceDep,
):
    conversation = await service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversation not found',
        )
    return conversation


@router.post(
    '/',
    response_model=ConversationPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_conversation(
    payload: ConversationCreate,
    _: ConversationCreateAuth,
    service: ConversationServiceDep,
):
    return await service.create_conversation(payload)


@router.patch('/{conversation_id}', response_model=ConversationPublic)
async def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    _: ConversationUpdateAuth,
    service: ConversationServiceDep,
):
    conversation = await service.update_conversation(conversation_id, payload)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversation not found',
        )
    return conversation
