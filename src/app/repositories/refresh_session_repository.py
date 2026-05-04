from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.refresh import RefreshSession
from src.app.repositories.base import BaseRepository


class RefreshSessionRepository(BaseRepository[RefreshSession]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=RefreshSession)

    async def list_by_user(self, user_id: UUID) -> list[RefreshSession]:
        return await self.get_all(user_id=user_id)

    async def get_by_refresh_token_id(
        self,
        refresh_token_id: UUID,
    ) -> RefreshSession | None:
        sessions = await self.get_all(refresh_token_id=refresh_token_id)
        return sessions[0] if sessions else None
