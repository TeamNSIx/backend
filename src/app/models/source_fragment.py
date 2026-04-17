from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.models.base_model import BaseModel


class SourceFragment(BaseModel, table=True):
    __tablename__ = 'source_fragments'

    source_id: UUID = Field(foreign_key='sources.id')
    content: str
    chunk_index: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
