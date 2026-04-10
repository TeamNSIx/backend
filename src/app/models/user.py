from enum import Enum
<<<<<<< HEAD
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.conversation import Conversation
    from src.app.models.query_log import QueryLog
=======
from typing import Optional

from sqlmodel import Field

from app.models.base_model import BaseModel
>>>>>>> b48911e (Feature/database setup (#9))


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'


<<<<<<< HEAD
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


class UserPublic(UserBase, BaseModel):
    pass
=======
class User(BaseModel, table=True):
    __tablename__ = 'users'

    email: Optional[str] = Field(default=None, index=True)
    role: UserRole = Field(default=UserRole.USER)
    full_name: Optional[str] = None
    study_group: Optional[str] = None
    faculty: Optional[str] = None
>>>>>>> b48911e (Feature/database setup (#9))
