from uuid import UUID

from pydantic import BaseModel, Field, model_validator

from src.app.models.embedding import EmbeddingPublic
from src.app.models.source import SourceType
from src.app.models.source_fragment import SourceFragmentPublic


class KnowledgeFragmentCreate(BaseModel):
    content: str = Field(min_length=1)
    source_id: UUID | None = None
    source_url: str | None = None
    source_title: str | None = None
    source_type: SourceType = SourceType.DOCUMENT
    chunk_index: int | None = None

    @model_validator(mode='after')
    def validate_source(self) -> 'KnowledgeFragmentCreate':
        if self.source_id is None and self.source_url is None:
            msg = 'source_id or source_url is required'
            raise ValueError(msg)
        return self


class KnowledgeFragmentResponse(BaseModel):
    fragment: SourceFragmentPublic
    embedding: EmbeddingPublic


class KnowledgeUrlIngestCreate(BaseModel):
    url: str = Field(min_length=1)
    title: str | None = None


class KnowledgeUrlIngestResponse(BaseModel):
    source_url: str
    source_title: str
    content_hash: str
    chunks_indexed: int
