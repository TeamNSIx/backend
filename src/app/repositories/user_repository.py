from sqlalchemy.ext.asyncio import AsyncSession

from src.app.models.user import User
from src.app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(session=session, model=User)

    async def get_by_email(self, email: str) -> User | None:
        users = await self.get_all(email=email)
        return users[0] if users else None
