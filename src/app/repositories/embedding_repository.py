from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.embedding import Embedding
from src.app.repositories.base import BaseRepository


class EmbeddingRepository(BaseRepository[Embedding]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Embedding)

    async def list_by_fragment(self, fragment_id: UUID) -> list[Embedding]:
        return await self.get_all(fragment_id=fragment_id)
