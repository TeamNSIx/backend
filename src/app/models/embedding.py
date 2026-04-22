<<<<<<< HEAD
<<<<<<< HEAD
from typing import TYPE_CHECKING
=======
from typing import Optional
>>>>>>> b48911e (Feature/database setup (#9))
=======
from typing import TYPE_CHECKING
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
from uuid import UUID

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column
<<<<<<< HEAD
<<<<<<< HEAD
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.source_fragment import SourceFragment
=======
from sqlmodel import Field

from app.models.base_model import BaseModel
>>>>>>> b48911e (Feature/database setup (#9))
=======
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

if TYPE_CHECKING:
    from src.app.models.source_fragment import SourceFragment
>>>>>>> 8712bd2 (Feature/database&migrations (#11))

EMBEDDING_PARAM = 1536


<<<<<<< HEAD
<<<<<<< HEAD
=======
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
class EmbeddingBase(SQLModel):
    fragment_id: UUID = Field(foreign_key='source_fragments.id')
    embedding: list | None = Field(sa_column=Column(Vector(EMBEDDING_PARAM)))
    model_name: str | None = None


class Embedding(EmbeddingBase, BaseModel, table=True):
<<<<<<< HEAD
    __tablename__ = 'embeddings'

    fragment: 'SourceFragment' = Relationship(back_populates='embeddings')


class EmbeddingCreate(EmbeddingBase):
    pass


class EmbeddingUpdate(SQLModel):
    embedding: list | None = None
    model_name: str | None = None


class EmbeddingPublic(EmbeddingBase, BaseModel):
    pass
=======
class Embedding(BaseModel, table=True):
    __tablename__ = 'embeddings'

    fragment_id: UUID = Field(foreign_key='source_fragments.id')
    embedding: Optional[list] = Field(sa_column=Column(Vector(EMBEDDING_PARAM)))
    model_name: Optional[str] = None
>>>>>>> b48911e (Feature/database setup (#9))
=======
    __tablename__ = 'embeddings'

    fragment: 'SourceFragment' = Relationship(back_populates='embeddings')


class EmbeddingCreate(EmbeddingBase):
    pass


class EmbeddingUpdate(SQLModel):
    embedding: list | None = None
    model_name: str | None = None


class EmbeddingPublic(EmbeddingBase, BasePublic):
    pass
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
