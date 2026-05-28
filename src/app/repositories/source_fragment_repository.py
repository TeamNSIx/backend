from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.db.database import get_session
from src.app.models.source_fragment import SourceFragment
from src.app.repositories.base import BaseRepository


class SourceFragmentRepository(BaseRepository[SourceFragment]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=SourceFragment)

    async def list_by_source(self, source_id: UUID) -> list[SourceFragment]:
        return await self.get_all(source_id=source_id)

    async def list_active_by_source(self, source_id: UUID) -> list[SourceFragment]:
        result = await self.session.execute(
            select(SourceFragment).where(
                SourceFragment.source_id == source_id,
                SourceFragment.valid_to.is_(None),
            ),
        )
        return list(result.scalars().all())

    async def expire_active_by_source(self, source_id: UUID) -> None:
        await self.session.execute(
            update(SourceFragment)
            .where(
                SourceFragment.source_id == source_id,
                SourceFragment.valid_to.is_(None),
            )
            .values(valid_to=func.now()),
        )
