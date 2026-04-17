from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.models.base_model import BaseModel


class Conversation(BaseModel, table=True):
    __tablename__ = 'conversations'

    user_id: UUID = Field(foreign_key='users.id')
    title: Optional[str] = None
    is_finished: bool = Field(default=True)
