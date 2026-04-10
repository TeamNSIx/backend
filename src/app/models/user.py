from enum import Enum
from typing import Optional

from sqlmodel import Field

from app.models.base_model import BaseModel


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'
    MODERATOR = 'moderator'


class User(BaseModel, table=True):
    __tablename__ = 'users'

    email: Optional[str] = Field(default=None, index=True)
    role: UserRole = Field(default=UserRole.USER)
    full_name: Optional[str] = None
    study_group: Optional[str] = None
    faculty: Optional[str] = None
