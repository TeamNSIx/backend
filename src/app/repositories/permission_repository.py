from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import get_session
from src.app.models.rbac_models import Permission
from src.app.repositories.base import BaseRepository


class PermissionRepository(BaseRepository[Permission]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        super().__init__(session=session, model=Permission)

    async def get_by_subject_action(
        self,
        subject: str,
        action: str,
    ) -> Permission | None:
        permissions = await self.get_all(subject=subject, action=action)
        return permissions[0] if permissions else None
