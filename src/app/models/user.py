from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

if TYPE_CHECKING:
    from src.app.models.conversation import Conversation
    from src.app.models.query_log import QueryLog


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'


class UserBase(SQLModel):
    email: str | None = Field(default=None, index=True)
    role: UserRole = Field(default=UserRole.USER)
    full_name: str | None = None
    study_group: str | None = None
    faculty: str | None = None


class User(UserBase, BaseModel, table=True):
    __tablename__ = 'users'

    conversations: list['Conversation'] = Relationship(back_populates='user')
    query_logs: list['QueryLog'] = Relationship(back_populates='user')


class UserCreate(UserBase):
    pass


class UserUpdate(SQLModel):
    email: str | None = None
    role: UserRole | None = None
    full_name: str | None = None
    study_group: str | None = None
    faculty: str | None = None


class UserPublic(UserBase, BasePublic):
    pass
