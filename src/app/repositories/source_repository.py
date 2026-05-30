from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.db.database import get_session
from src.app.models.source import Source
from src.app.repositories.base import BaseRepository


class SourceRepository(BaseRepository[Source]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=Source)

    async def get_by_url(self, url: str) -> Source | None:
        result = await self.session.execute(select(Source).where(Source.url == url))
        return result.scalar_one_or_none()
