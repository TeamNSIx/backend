from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.db.database import get_session
from src.app.models.rbac_models import UserRoleLink


class UserRoleLinkRepository:
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> None:
        self.session = session

    async def get_link(self, user_id: UUID, role_id: UUID) -> UserRoleLink | None:
        stmt = select(UserRoleLink).where(
            UserRoleLink.user_id == user_id,
            UserRoleLink.role_id == role_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def add_link(self, user_id: UUID, role_id: UUID) -> None:
        self.session.add(UserRoleLink(user_id=user_id, role_id=role_id))
        await self.session.commit()

    async def replace_user_roles(self, user_id: UUID, role_ids: list[UUID]) -> None:
        await self.session.execute(
            delete(UserRoleLink).where(UserRoleLink.user_id == user_id),
        )
        for role_id in role_ids:
            self.session.add(UserRoleLink(user_id=user_id, role_id=role_id))
        await self.session.commit()
