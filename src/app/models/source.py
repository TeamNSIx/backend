from datetime import datetime
from enum import Enum
<<<<<<< HEAD
from typing import TYPE_CHECKING

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.source_fragment import SourceFragment
=======
from typing import Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base_model import BaseModel
>>>>>>> b48911e (Feature/database setup (#9))


class SourceType(str, Enum):
    WEBSITE = 'website'
    DOCUMENT = 'document'
    API = 'api'


<<<<<<< HEAD
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


class SourcePublic(SourceBase, BaseModel):
    pass
=======
class Source(BaseModel, table=True):
    __tablename__ = 'sources'

    url: str
    title: Optional[str] = None
    source_type: SourceType
    crawl_config: Optional[dict] = Field(sa_column=Column(JSONB))
    last_crawled_at: Optional[datetime] = None
    is_active: bool = True
>>>>>>> b48911e (Feature/database setup (#9))
