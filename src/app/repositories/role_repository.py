from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import get_session
from src.app.models.rbac_models import Role
from src.app.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        super().__init__(session=session, model=Role)

    async def get_by_name(self, name: str) -> Role | None:
        roles = await self.get_all(name=name)
        return roles[0] if roles else None
