from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.models.user import User
from src.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=User)

    async def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def update_fields(self, entity_id: UUID, updates: dict) -> User | None:
        user = await self.get_by_id(entity_id)
        if user is None:
            return None

        for key, value in updates.items():
            setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user
