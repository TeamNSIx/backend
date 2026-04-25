from enum import Enum
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

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
<<<<<<< HEAD
<<<<<<< HEAD
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.conversation import Conversation
    from src.app.models.response_log import ResponseLog
=======
from sqlmodel import Field

from app.models.base_model import BaseModel
>>>>>>> b48911e (Feature/database setup (#9))
=======
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.conversation import Conversation
    from src.app.models.response_log import ResponseLog
>>>>>>> 8712bd2 (Feature/database&migrations (#11))


class MessageSender(str, Enum):
    USER = 'user'
    SYSTEM = 'system'


<<<<<<< HEAD
<<<<<<< HEAD
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


class MessagePublic(MessageBase, BaseModel):
    pass
=======
class Message(BaseModel, table=True):
    __tablename__ = 'messages'

    conversation_id: UUID = Field(foreign_key='conversations.id')
    sender: MessageSender
    content: str
    message_metadata: Optional[dict] = Field(sa_column=Column(JSONB))
>>>>>>> b48911e (Feature/database setup (#9))
=======
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


class MessagePublic(MessageBase, BaseModel):
    pass
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
