<<<<<<< HEAD
<<<<<<< HEAD
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.feedback import Feedback
    from src.app.models.message import Message
    from src.app.models.user import User


class ConversationBase(SQLModel):
    user_id: UUID = Field(foreign_key='users.id')
    title: Optional[str] = None
    is_finished: bool = Field(default=True)


class Conversation(ConversationBase, BaseModel, table=True):
    __tablename__ = 'conversations'

    user: 'User' = Relationship(back_populates='conversations')
    messages: list['Message'] = Relationship(back_populates='conversation')
    feedback_entries: list['Feedback'] = Relationship(back_populates='conversation')


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(SQLModel):
    title: str | None = None
    is_finished: bool | None = None


class ConversationPublic(ConversationBase, BaseModel):
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
    from src.app.models.feedback import Feedback
    from src.app.models.message import Message
    from src.app.models.user import User


class ConversationBase(SQLModel):
    user_id: UUID = Field(foreign_key='users.id')
    title: str | None = None
    is_finished: bool = Field(default=True)


class Conversation(ConversationBase, BaseModel, table=True):
    __tablename__ = 'conversations'

<<<<<<< HEAD
    user_id: UUID = Field(foreign_key='users.id')
    title: Optional[str] = None
    is_finished: bool = Field(default=True)
>>>>>>> b48911e (Feature/database setup (#9))
=======
    user: 'User' = Relationship(back_populates='conversations')
    messages: list['Message'] = Relationship(back_populates='conversation')
    feedback_entries: list['Feedback'] = Relationship(back_populates='conversation')


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(SQLModel):
    title: str | None = None
    is_finished: bool | None = None


class ConversationPublic(ConversationBase, BasePublic):
    pass
>>>>>>> 8712bd2 (Feature/database&migrations (#11))
