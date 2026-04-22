from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import get_session
from src.app.repositories.conversation_repository import ConversationRepository
from src.app.repositories.user_repository import UserRepository
from src.app.services.conversation_service import ConversationService
from src.app.services.user_service import UserService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_conversation_repository(session: SessionDep) -> ConversationRepository:
    return ConversationRepository(session)


def get_user_service(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(user_repository)


def get_conversation_service(
    conversation_repository: Annotated[
        ConversationRepository, Depends(get_conversation_repository)
    ],
) -> ConversationService:
    return ConversationService(conversation_repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ConversationServiceDep = Annotated[
    ConversationService, Depends(get_conversation_service)
]
