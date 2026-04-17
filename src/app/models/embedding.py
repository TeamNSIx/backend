from typing import Optional
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
from sqlmodel import Field

from app.models.base_model import BaseModel

EMBEDDING_PARAM = 1536


class Embedding(BaseModel, table=True):
    __tablename__ = 'embeddings'

    fragment_id: UUID = Field(foreign_key='source_fragments.id')
    embedding: Optional[list] = Field(sa_column=Column(Vector(EMBEDDING_PARAM)))
    model_name: Optional[str] = None
