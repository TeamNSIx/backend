from uuid import UUID

from src.app.models.response_log import (
    ResponseLog,
    ResponseLogCreate,
    ResponseLogPublic,
    ResponseLogUpdate,
)
from src.app.repositories.response_log_repository import ResponseLogRepository


class ResponseLogService:
    def __init__(self, repository: ResponseLogRepository) -> None:
        self.repository = repository

    async def list_response_logs(
        self,
        message_id: UUID | None = None,
        query_log_id: UUID | None = None,
    ) -> list[ResponseLogPublic]:
        if message_id is not None:
            response_logs = await self.repository.list_by_message(message_id)
        elif query_log_id is not None:
            response_logs = await self.repository.list_by_query_log(query_log_id)
        else:
            response_logs = await self.repository.get_all()
        return [ResponseLogPublic.model_validate(response_log) for response_log in response_logs]

    async def get_response_log(self, response_log_id: UUID) -> ResponseLogPublic | None:
        response_log = await self.repository.get_by_id(response_log_id)
        if response_log is None:
            return None
        return ResponseLogPublic.model_validate(response_log)

    async def create_response_log(self, payload: ResponseLogCreate) -> ResponseLogPublic:
        response_log = ResponseLog.model_validate(payload)
        created = await self.repository.add(response_log)
        return ResponseLogPublic.model_validate(created)

    async def update_response_log(
        self,
        response_log_id: UUID,
        payload: ResponseLogUpdate,
    ) -> ResponseLogPublic | None:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(response_log_id, updates)
        if updated is None:
            return None
        return ResponseLogPublic.model_validate(updated)
