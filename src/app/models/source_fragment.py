from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class SourceFragment(SQLModel, table=True):
    __tablename__ = 'source_fragments'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    source_id: UUID = Field(foreign_key='sources.id')

    content: str

    chunk_index: Optional[int] = None

    valid_from: Optional[datetime] = None

    valid_to: Optional[datetime] = None

    created_at: datetime | None
