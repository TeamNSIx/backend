from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.app.models.feedback import Feedback, FeedbackCreate, FeedbackPublic
from src.app.repositories.feedback_repository import FeedbackRepository


class FeedbackService:
    def __init__(
        self,
        repository: Annotated[FeedbackRepository, Depends(FeedbackRepository)],
    ) -> None:
        self.repository = repository

    async def list_feedback(
        self,
        conversation_id: UUID | None = None,
    ) -> list[FeedbackPublic]:
        if conversation_id is None:
            feedback_entries = await self.repository.get_all()
        else:
            feedback_entries = await self.repository.list_by_conversation(
                conversation_id,
            )
        return [FeedbackPublic.model_validate(item) for item in feedback_entries]

    async def create_feedback(self, payload: FeedbackCreate) -> FeedbackPublic:
        feedback = Feedback.model_validate(payload)
        created = await self.repository.add(feedback)
        return FeedbackPublic.model_validate(created)
