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
    from src.app.models.message import Message
    from src.app.models.query_log import QueryLog


class ResponseLogBase(SQLModel):
    message_id: UUID = Field(foreign_key='messages.id')
    query_log_id: UUID = Field(foreign_key='query_logs.id')
    response_text: str
    used_fragments: dict | None = Field(sa_column=Column(JSONB))
    response_time_ms: int | None = None
    user_helpful: bool | None = None


class ResponseLog(ResponseLogBase, BaseModel, table=True):
    __tablename__ = 'response_logs'

    message: 'Message' = Relationship(back_populates='response_logs')
    query_log: 'QueryLog' = Relationship(back_populates='response_logs')


class ResponseLogCreate(ResponseLogBase):
    pass


class ResponseLogUpdate(SQLModel):
    response_text: str | None = None
    used_fragments: dict | None = None
    response_time_ms: int | None = None
    user_helpful: bool | None = None


class ResponseLogPublic(ResponseLogBase, BaseModel):
    pass
=======
from sqlmodel import Field

from app.models.base_model import BaseModel


class ResponseLog(BaseModel, table=True):
    __tablename__ = 'response_logs'

    message_id: UUID = Field(foreign_key='messages.id')
    query_log_id: UUID = Field(foreign_key='query_logs.id')
    response_text: str
    used_fragments: Optional[dict] = Field(sa_column=Column(JSONB))
    response_time_ms: Optional[int] = None
    user_helpful: Optional[bool] = None
>>>>>>> b48911e (Feature/database setup (#9))
