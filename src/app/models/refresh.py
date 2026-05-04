from datetime import datetime, timezone
from uuid import UUID

from pydantic import computed_field
from sqlmodel import Field, SQLModel

from src.app.models.base_model import BaseModel


class RefreshSessionCreate(SQLModel):
    user_id: UUID = Field(foreign_key='users.id')
    access_token_id: UUID
    refresh_token_id: UUID
    expires_at: datetime


class RefreshSession(RefreshSessionCreate, BaseModel, table=True):
    __tablename__ = 'refresh_sessions'

    is_invalidated: bool = Field(default=False)

    @computed_field
    @property
    def is_valid(self) -> bool:
        now = datetime.now(timezone.utc)
        expired = now > self.expires_at
        is_invalid = expired or self.is_invalidated
        return not is_invalid