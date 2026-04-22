from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

if TYPE_CHECKING:
    from src.app.models.source_fragment import SourceFragment


class SourceType(str, Enum):
    WEBSITE = 'website'
    DOCUMENT = 'document'
    API = 'api'


class SourceBase(SQLModel):
    url: str
    title: str | None = None
    source_type: SourceType
    crawl_config: dict | None = Field(sa_column=Column(JSONB))
    last_crawled_at: datetime | None = None
    is_active: bool = True


class Source(SourceBase, BaseModel, table=True):
    __tablename__ = 'sources'

    fragments: list['SourceFragment'] = Relationship(back_populates='source')


class SourceCreate(SourceBase):
    pass


class SourceUpdate(SQLModel):
    url: str | None = None
    title: str | None = None
    source_type: SourceType | None = None
    crawl_config: dict | None = None
    last_crawled_at: datetime | None = None
    is_active: bool | None = None


class SourcePublic(SourceBase, BasePublic):
    pass
