from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

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


class ResponseLogPublic(ResponseLogBase, BasePublic):
    pass
