from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Feedback(SQLModel, table=True):
    __tablename__ = 'feedback'

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    conversation_id: UUID = Field(foreign_key='conversations.id')

    rating: Optional[int] = None

    comment: Optional[str] = None

    created_at: datetime | None
