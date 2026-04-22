from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

if TYPE_CHECKING:
    from src.app.models.conversation import Conversation
    from src.app.models.response_log import ResponseLog


class MessageSender(str, Enum):
    USER = 'user'
    SYSTEM = 'system'


class MessageBase(SQLModel):
    conversation_id: UUID = Field(foreign_key='conversations.id')
    sender: MessageSender
    content: str
    message_metadata: dict | None = Field(sa_column=Column(JSONB))


class Message(MessageBase, BaseModel, table=True):
    __tablename__ = 'messages'

    conversation: 'Conversation' = Relationship(back_populates='messages')
    response_logs: list['ResponseLog'] = Relationship(back_populates='message')


class MessageCreate(MessageBase):
    pass


class MessageUpdate(SQLModel):
    content: str | None = None
    message_metadata: dict | None = None


class MessagePublic(MessageBase, BasePublic):
    pass
