from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.source_fragment import SourceFragment
from src.app.repositories.base import BaseRepository


class SourceFragmentRepository(BaseRepository[SourceFragment]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=SourceFragment)

    async def list_by_source(self, source_id: UUID) -> list[SourceFragment]:
        return await self.get_all(source_id=source_id)
