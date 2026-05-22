from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.app.models.feedback import Feedback, FeedbackCreate, FeedbackPublic
from src.app.repositories.feedback_repository import FeedbackRepository
from src.app.schemas.pagination import PaginatedResponse, PaginationParams


class FeedbackService:
    def __init__(
        self,
        repository: Annotated[FeedbackRepository, Depends(FeedbackRepository)],
    ) -> None:
        self.repository = repository

    async def list_feedback(
        self,
        conversation_id: UUID,
        pagination: PaginationParams,
    ) -> PaginatedResponse[FeedbackPublic]:
        total = await self.repository.count(conversation_id=conversation_id)
        feedback_entries = await self.repository.get_page(
            pagination.offset,
            pagination.page_size,
            order_asc=True,
            conversation_id=conversation_id,
        )
        items = [FeedbackPublic.model_validate(item) for item in feedback_entries]
        return PaginatedResponse.build(items, total, pagination)

    async def create_feedback(self, payload: FeedbackCreate) -> FeedbackPublic:
        feedback = Feedback.model_validate(payload)
        created = await self.repository.add(feedback)
        return FeedbackPublic.model_validate(created)
