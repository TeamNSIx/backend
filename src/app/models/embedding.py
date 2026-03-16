from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field, SQLModel


class Embedding(SQLModel, table=True):
    __tablename__ = 'embeddings'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    fragment_id: UUID = Field(foreign_key='source_fragments.id')

    embedding: Optional[list] = Field(sa_column=Column(Vector(1536)))

    model_name: Optional[str] = None

    created_at: datetime | None
