from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import Vector
from pydantic import field_serializer
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.source_fragment import SourceFragment

EMBEDDING_PARAM = 384


class EmbeddingBase(SQLModel):
    fragment_id: UUID = Field(foreign_key='source_fragments.id')
    embedding: list | None = Field(sa_column=Column(Vector(EMBEDDING_PARAM)))
    model_name: str | None = None

    @field_serializer('embedding')
    def serialize_embedding(self, value: list | None) -> list[float] | None:
        if value is None:
            return None
        return [float(item) for item in value]


class Embedding(EmbeddingBase, BaseModel, table=True):
    __tablename__ = 'embeddings'

    fragment: 'SourceFragment' = Relationship(back_populates='embeddings')


class EmbeddingCreate(EmbeddingBase):
    pass


class EmbeddingUpdate(SQLModel):
    embedding: list | None = None
    model_name: str | None = None


class EmbeddingPublic(EmbeddingBase, BaseModel):
    pass
