from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.source import Source
from src.app.repositories.base import BaseRepository


class SourceRepository(BaseRepository[Source]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=Source)
