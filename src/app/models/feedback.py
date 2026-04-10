from typing import Optional
from uuid import UUID

from sqlmodel import Field

from app.models.base_model import BaseModel


class Feedback(BaseModel, table=True):
    __tablename__ = 'feedback'

    conversation_id: UUID = Field(foreign_key='conversations.id')
    rating: Optional[int] = None
    comment: Optional[str] = None
