from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel

from .enums import UserRole


class User(SQLModel, table=True):
    __tablename__ = 'users'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    email: Optional[str] = Field(default=None, index=True)
    telegram_id: Optional[str] = Field(default=None, index=True)

    role: UserRole

    full_name: Optional[str] = None
    study_group: Optional[str] = None
    faculty: Optional[str] = None

    created_at: datetime | None
