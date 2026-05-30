from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Security, status

from src.app.core.responses import auth_responses, common_responses, merge_responses
from src.app.dependencies import SourceFragmentServiceDep, SourceServiceDep
from src.app.dependencies.auth import get_current_user
from src.app.models.embedding import EmbeddingPublic
from src.app.models.source import SourceCreate
from src.app.models.source_fragment import SourceFragmentCreate
from src.app.schemas.knowledge import (
    KnowledgeFragmentCreate,
    KnowledgeFragmentResponse,
    KnowledgeUrlIngestCreate,
    KnowledgeUrlIngestResponse,
)
from src.app.services.rag_service import RAGService
from src.app.services.web_ingestion_service import WebIngestionService
from src.utils.error import NotFoundError

router = APIRouter(prefix='/knowledge', tags=['knowledge'])

_responses = merge_responses(common_responses, auth_responses)
knowledge_write_dependency = Security(get_current_user, scopes=['profile:create'])
RAGServiceDep = Annotated[RAGService, Depends(RAGService)]
WebIngestionServiceDep = Annotated[WebIngestionService, Depends(WebIngestionService)]


@router.post(
    '/fragments',
    status_code=status.HTTP_201_CREATED,
    responses=_responses,
    dependencies=[knowledge_write_dependency],
)
async def create_fragment(
    payload: KnowledgeFragmentCreate,
    source_service: SourceServiceDep,
    fragment_service: SourceFragmentServiceDep,
    rag_service: RAGServiceDep,
) -> KnowledgeFragmentResponse:
    source_id = payload.source_id
    if source_id is None:
        source = await source_service.create_source(
            SourceCreate(
                url=payload.source_url or '',
                title=payload.source_title,
                source_type=payload.source_type,
            ),
        )
        source_id = source.id

    fragment = await fragment_service.create_fragment(
        SourceFragmentCreate(
            source_id=source_id,
            content=payload.content,
            chunk_index=payload.chunk_index,
        ),
    )
    embedding = await rag_service.create_fragment_embedding(fragment)
    return KnowledgeFragmentResponse(
        fragment=fragment,
        embedding=EmbeddingPublic.model_validate(embedding),
    )


@router.post(
    '/sources/ingest-url',
    status_code=status.HTTP_201_CREATED,
    responses=_responses,
    dependencies=[knowledge_write_dependency],
)
async def ingest_url(
    payload: KnowledgeUrlIngestCreate,
    web_ingestion_service: WebIngestionServiceDep,
) -> KnowledgeUrlIngestResponse:
    context = await web_ingestion_service.ingest_url(payload.url, payload.title)
    return KnowledgeUrlIngestResponse(
        source_url=context.source_url,
        source_title=context.source_title,
        content_hash=context.content_hash,
        chunks_indexed=len(context.chunks),
    )


@router.post(
    '/fragments/{fragment_id}/embedding',
    responses=_responses,
    dependencies=[knowledge_write_dependency],
)
async def refresh_fragment_embedding(
    fragment_id: UUID,
    fragment_service: SourceFragmentServiceDep,
    rag_service: RAGServiceDep,
) -> EmbeddingPublic:
    fragment = await fragment_service.get_fragment(fragment_id)
    if fragment is None:
        raise NotFoundError(detail='Source fragment not found')
    embedding = await rag_service.create_fragment_embedding(fragment)
    return EmbeddingPublic.model_validate(embedding)
