from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.app.db.database import get_session
from src.app.models.rbac_models import Role
from src.app.models.user import User
from src.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=User)

    async def get_by_email(self, email: str) -> User | None:
        users = await self.get_all(email=email)
        return users[0] if users else None

    async def get_with_roles(self, user_id: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.rbac_roles).selectinload(Role.permissions))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
