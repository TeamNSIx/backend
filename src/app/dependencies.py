from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import get_session
from src.app.repositories.conversation_repository import ConversationRepository
from src.app.repositories.embedding_repository import EmbeddingRepository
from src.app.repositories.query_log_repository import QueryLogRepository
from src.app.repositories.response_log_repository import ResponseLogRepository
from src.app.repositories.source_fragment_repository import SourceFragmentRepository
from src.app.repositories.source_repository import SourceRepository
from src.app.repositories.user_repository import UserRepository
from src.app.services.conversation_service import ConversationService
from src.app.services.embedding_service import EmbeddingService
from src.app.services.query_log_service import QueryLogService
from src.app.services.response_log_service import ResponseLogService
from src.app.services.source_fragment_service import SourceFragmentService
from src.app.services.source_service import SourceService
from src.app.services.user_service import UserService

SessionDep = Annotated[AsyncSession, Depends(get_session)]


def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


def get_conversation_repository(session: SessionDep) -> ConversationRepository:
    return ConversationRepository(session)


def get_source_repository(session: SessionDep) -> SourceRepository:
    return SourceRepository(session)


def get_source_fragment_repository(session: SessionDep) -> SourceFragmentRepository:
    return SourceFragmentRepository(session)


def get_embedding_repository(session: SessionDep) -> EmbeddingRepository:
    return EmbeddingRepository(session)


def get_query_log_repository(session: SessionDep) -> QueryLogRepository:
    return QueryLogRepository(session)


def get_response_log_repository(session: SessionDep) -> ResponseLogRepository:
    return ResponseLogRepository(session)


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


def get_source_service(
    source_repository: Annotated[SourceRepository, Depends(get_source_repository)],
) -> SourceService:
    return SourceService(source_repository)


def get_source_fragment_service(
    source_fragment_repository: Annotated[
        SourceFragmentRepository, Depends(get_source_fragment_repository)
    ],
) -> SourceFragmentService:
    return SourceFragmentService(source_fragment_repository)


def get_embedding_service(
    embedding_repository: Annotated[EmbeddingRepository, Depends(get_embedding_repository)],
) -> EmbeddingService:
    return EmbeddingService(embedding_repository)


def get_query_log_service(
    query_log_repository: Annotated[QueryLogRepository, Depends(get_query_log_repository)],
) -> QueryLogService:
    return QueryLogService(query_log_repository)


def get_response_log_service(
    response_log_repository: Annotated[
        ResponseLogRepository, Depends(get_response_log_repository)
    ],
) -> ResponseLogService:
    return ResponseLogService(response_log_repository)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
ConversationServiceDep = Annotated[
    ConversationService, Depends(get_conversation_service)
]
SourceServiceDep = Annotated[SourceService, Depends(get_source_service)]
SourceFragmentServiceDep = Annotated[
    SourceFragmentService, Depends(get_source_fragment_service)
]
EmbeddingServiceDep = Annotated[EmbeddingService, Depends(get_embedding_service)]
QueryLogServiceDep = Annotated[QueryLogService, Depends(get_query_log_service)]
ResponseLogServiceDep = Annotated[ResponseLogService, Depends(get_response_log_service)]
