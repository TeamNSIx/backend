from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base_model import BaseModel


class SourceType(str, Enum):
    WEBSITE = 'website'
    DOCUMENT = 'document'
    API = 'api'


class Source(BaseModel, table=True):
    __tablename__ = 'sources'

    url: str
    title: Optional[str] = None
    source_type: SourceType
    crawl_config: Optional[dict] = Field(sa_column=Column(JSONB))
    last_crawled_at: Optional[datetime] = None
    is_active: bool = True
