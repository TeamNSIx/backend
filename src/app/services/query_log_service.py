from uuid import UUID

from src.app.models.query_log import QueryLog, QueryLogCreate, QueryLogPublic, QueryLogUpdate
from src.app.repositories.query_log_repository import QueryLogRepository


class QueryLogService:
    def __init__(self, repository: QueryLogRepository) -> None:
        self.repository = repository

    async def list_query_logs(self, user_id: UUID | None = None) -> list[QueryLogPublic]:
        if user_id is None:
            query_logs = await self.repository.get_all()
        else:
            query_logs = await self.repository.list_by_user(user_id)
        return [QueryLogPublic.model_validate(query_log) for query_log in query_logs]

    async def get_query_log(self, query_log_id: UUID) -> QueryLogPublic | None:
        query_log = await self.repository.get_by_id(query_log_id)
        if query_log is None:
            return None
        return QueryLogPublic.model_validate(query_log)

    async def create_query_log(self, payload: QueryLogCreate) -> QueryLogPublic:
        query_log = QueryLog.model_validate(payload)
        created = await self.repository.add(query_log)
        return QueryLogPublic.model_validate(created)

    async def update_query_log(
        self,
        query_log_id: UUID,
        payload: QueryLogUpdate,
    ) -> QueryLogPublic | None:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(query_log_id, updates)
        if updated is None:
            return None
        return QueryLogPublic.model_validate(updated)
