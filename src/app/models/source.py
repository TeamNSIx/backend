from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class Source(SQLModel, table=True):
    __tablename__ = 'sources'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    url: str

    title: Optional[str] = None

    class SourceType(str, Enum):
        WEBSITE = 'website'
        DOCUMENT = 'document'
        API = 'api'

    source_type: SourceType

    crawl_config: Optional[dict] = Field(sa_column=Column(JSONB))

    last_crawled_at: Optional[datetime] = None

    is_active: bool = True
