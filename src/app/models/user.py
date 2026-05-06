from enum import Enum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel
from src.app.models.rbac_models import UserRoleLink

if TYPE_CHECKING:
    from src.app.models.conversation import Conversation
    from src.app.models.query_log import QueryLog
    from src.app.models.rbac_models import Role


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

    password_hash: str | None = None
    conversations: list['Conversation'] = Relationship(back_populates='user')
    query_logs: list['QueryLog'] = Relationship(back_populates='user')
    rbac_roles: list['Role'] = Relationship(
        back_populates='users',
        link_model=UserRoleLink,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )


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
