from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import get_session
from src.app.models.query_log import QueryLog
from src.app.repositories.base import BaseRepository


class QueryLogRepository(BaseRepository[QueryLog]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=QueryLog)

    async def list_by_user(self, user_id: UUID) -> list[QueryLog]:
        return await self.get_all(user_id=user_id)
