from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class MessageSender(str, Enum):
    USER = 'user'
    BOT = 'bot'
    SYSTEM = 'system'


class Message(SQLModel, table=True):
    __tablename__ = 'messages'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    conversation_id: UUID = Field(foreign_key='conversations.id')

    sender: MessageSender

    content: str

    metadata: Optional[dict] = Field(sa_column=Column(JSONB))

    created_at: datetime | None
