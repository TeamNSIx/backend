from datetime import datetime
<<<<<<< HEAD
<<<<<<< HEAD
from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.embedding import Embedding
    from src.app.models.source import Source


class SourceFragmentBase(SQLModel):
    source_id: UUID = Field(foreign_key='sources.id')
    content: str
    chunk_index: int | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class SourceFragment(SourceFragmentBase, BaseModel, table=True):
    __tablename__ = 'source_fragments'

    source: 'Source' = Relationship(back_populates='fragments')
    embeddings: list['Embedding'] = Relationship(back_populates='fragment')


class SourceFragmentCreate(SourceFragmentBase):
    pass


class SourceFragmentUpdate(SQLModel):
    content: str | None = None
    chunk_index: int | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class SourceFragmentPublic(SourceFragmentBase, BaseModel):
    pass
=======
from typing import Optional
=======
from typing import TYPE_CHECKING
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

if TYPE_CHECKING:
    from src.app.models.embedding import Embedding
    from src.app.models.source import Source


class SourceFragmentBase(SQLModel):
    source_id: UUID = Field(foreign_key='sources.id')
    content: str
<<<<<<< HEAD
    chunk_index: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
>>>>>>> b48911e (Feature/database setup (#9))
=======
    chunk_index: int | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class SourceFragment(SourceFragmentBase, BaseModel, table=True):
    __tablename__ = 'source_fragments'

    source: 'Source' = Relationship(back_populates='fragments')
    embeddings: list['Embedding'] = Relationship(back_populates='fragment')


class SourceFragmentCreate(SourceFragmentBase):
    pass


class SourceFragmentUpdate(SQLModel):
    content: str | None = None
    chunk_index: int | None = None
    valid_from: datetime | None = None
    valid_to: datetime | None = None


class SourceFragmentPublic(SourceFragmentBase, BasePublic):
    pass
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
