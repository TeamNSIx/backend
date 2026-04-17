from enum import Enum
from typing import Optional
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base_model import BaseModel


class MessageSender(str, Enum):
    USER = 'user'
    SYSTEM = 'system'


class Message(BaseModel, table=True):
    __tablename__ = 'messages'

    conversation_id: UUID = Field(foreign_key='conversations.id')
    sender: MessageSender
    content: str
    message_metadata: Optional[dict] = Field(sa_column=Column(JSONB))
