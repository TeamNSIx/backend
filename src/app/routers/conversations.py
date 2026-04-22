from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from src.app.dependencies import ConversationServiceDep
from src.app.models.conversation import (
    ConversationCreate,
    ConversationPublic,
    ConversationUpdate,
)

router = APIRouter(prefix='/conversations', tags=['conversations'])


@router.get('/', response_model=list[ConversationPublic])
async def list_conversations(
    service: ConversationServiceDep,
    user_id: UUID | None = Query(default=None),
):
    return await service.list_conversations(user_id=user_id)


@router.get('/{conversation_id}', response_model=ConversationPublic)
async def get_conversation(conversation_id: UUID, service: ConversationServiceDep):
    conversation = await service.get_conversation(conversation_id)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversation not found',
        )
    return conversation


@router.post('/', response_model=ConversationPublic, status_code=status.HTTP_201_CREATED)
async def create_conversation(
    payload: ConversationCreate,
    service: ConversationServiceDep,
):
    return await service.create_conversation(payload)


@router.patch('/{conversation_id}', response_model=ConversationPublic)
async def update_conversation(
    conversation_id: UUID,
    payload: ConversationUpdate,
    service: ConversationServiceDep,
):
    conversation = await service.update_conversation(conversation_id, payload)
    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Conversation not found',
        )
    return conversation
