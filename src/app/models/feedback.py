from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel, BasePublic

if TYPE_CHECKING:
    from src.app.models.conversation import Conversation


class FeedbackBase(SQLModel):
    conversation_id: UUID = Field(foreign_key='conversations.id')
    rating: int | None = None
    comment: str | None = None


class Feedback(FeedbackBase, BaseModel, table=True):
    __tablename__ = 'feedback'

    conversation: 'Conversation' = Relationship(back_populates='feedback_entries')


class FeedbackCreate(FeedbackBase):
    pass


class FeedbackUpdate(SQLModel):
    rating: int | None = None
    comment: str | None = None


class FeedbackPublic(FeedbackBase, BasePublic):
    pass
