from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.response_log import ResponseLog
from src.app.repositories.base import BaseRepository


class ResponseLogRepository(BaseRepository[ResponseLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=ResponseLog)

    async def list_by_message(self, message_id: UUID) -> list[ResponseLog]:
        return await self.get_all(message_id=message_id)

    async def list_by_query_log(self, query_log_id: UUID) -> list[ResponseLog]:
        return await self.get_all(query_log_id=query_log_id)
