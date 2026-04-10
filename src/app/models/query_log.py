<<<<<<< HEAD
from typing import TYPE_CHECKING
=======
from typing import Optional
>>>>>>> b48911e (Feature/database setup (#9))
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
<<<<<<< HEAD
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.response_log import ResponseLog
    from src.app.models.user import User


class QueryLogBase(SQLModel):
    user_id: UUID = Field(foreign_key='users.id')
    query_text: str
    search_results: dict | None = Field(sa_column=Column(JSONB))


class QueryLog(QueryLogBase, BaseModel, table=True):
    __tablename__ = 'query_logs'

    user: 'User' = Relationship(back_populates='query_logs')
    response_logs: list['ResponseLog'] = Relationship(back_populates='query_log')


class QueryLogCreate(QueryLogBase):
    pass


class QueryLogUpdate(SQLModel):
    query_text: str | None = None
    search_results: dict | None = None


class QueryLogPublic(QueryLogBase, BaseModel):
    pass
=======
from sqlmodel import Field

from app.models.base_model import BaseModel


class QueryLog(BaseModel, table=True):
    __tablename__ = 'query_logs'

    user_id: UUID = Field(foreign_key='users.id')
    query_text: str
    search_results: Optional[dict] = Field(sa_column=Column(JSONB))
>>>>>>> b48911e (Feature/database setup (#9))
