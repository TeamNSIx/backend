from uuid import UUID

from src.app.models.user import User, UserCreate, UserPublic, UserUpdate
from src.app.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def list_users(self) -> list[UserPublic]:
        users = await self.repository.list_all()
        return [UserPublic.model_validate(user) for user in users]

    async def get_user(self, user_id: UUID) -> UserPublic | None:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            return None
        return UserPublic.model_validate(user)

    async def create_user(self, payload: UserCreate) -> UserPublic:
        user = User.model_validate(payload)
        created = await self.repository.add(user)
        return UserPublic.model_validate(created)

    async def update_user(self, user_id: UUID, payload: UserUpdate) -> UserPublic | None:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(user_id, updates)
        if updated is None:
            return None
        return UserPublic.model_validate(updated)
