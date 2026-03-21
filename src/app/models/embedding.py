from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel

EMBEDDING_PARAM = 1536


class Embedding(SQLModel, table=True):
    __tablename__ = 'embeddings'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fragment_id: UUID = Field(foreign_key='source_fragments.id')

    embedding: Optional[list] = Field(sa_column=Column(Vector(EMBEDDING_PARAM)))

    model_name: Optional[str] = None

    created_at: datetime | None
