from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

if TYPE_CHECKING:
    from src.app.models.embedding import Embedding
    from src.app.models.source import Source


class SourceFragmentBase(SQLModel):
    source_id: UUID = Field(foreign_key='sources.id')
    content: str
    chunk_index: int | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class SourceFragment(SourceFragmentBase, BaseModel, table=True):
    __tablename__ = 'source_fragments'

    source: 'Source' = Relationship(back_populates='fragments')
    embeddings: list['Embedding'] = Relationship(back_populates='fragment')


class SourceFragmentCreate(SourceFragmentBase):
    pass


class SourceFragmentUpdate(SQLModel):
    content: str | None = None
    chunk_index: int | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class SourceFragmentPublic(SourceFragmentBase, BasePublic):
    pass
