from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from .enums import SourceType


class Source(SQLModel, table=True):
    __tablename__ = 'sources'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    url: str

    title: Optional[str] = None

    source_type: SourceType

    crawl_config: Optional[dict] = Field(sa_column=Column(JSONB))

    last_crawled_at: Optional[datetime] = None

    is_active: bool = True
