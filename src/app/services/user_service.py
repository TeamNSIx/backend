from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.app.models.user import User, UserCreate, UserPublic, UserUpdate
from src.app.repositories.user_repository import UserRepository
from src.app.schemas.pagination import PaginatedResponse, PaginationParams
from src.app.services.refresh import RefreshSessionService
from src.utils.error import BadRequestError, NotFoundError, UnauthorizedError
from src.utils.hasher import Hasher


class UserService:
    def __init__(
        self,
        repository: Annotated[UserRepository, Depends(UserRepository)],
        refresh_session_service: Annotated[
            RefreshSessionService,
            Depends(RefreshSessionService),
        ],
    ) -> None:
        self.repository = repository
        self.refresh_session_service = refresh_session_service

    async def list_users(self, pagination: PaginationParams) -> PaginatedResponse[UserPublic]:
        total = await self.repository.count()
        users = await self.repository.get_page(
            pagination.offset,
            pagination.page_size,
        )
        items = [UserPublic.model_validate(user) for user in users]
        return PaginatedResponse.build(items, total, pagination)

    async def get_user(self, user_id: UUID) -> UserPublic:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(detail='User not found')
        return UserPublic.model_validate(user)

    async def create_user(self, payload: UserCreate) -> UserPublic:
        user = User.model_validate(payload)
        created = await self.repository.add(user)
        return UserPublic.model_validate(created)

    async def create_user_with_password(
        self,
        payload: UserCreate,
        plain_password: str,
        *,
        is_verified: bool = False,
    ) -> UserPublic:
        user = User.model_validate(payload)
        user.password_hash = Hasher.get_password_hash(plain_password)
        user.is_verified = is_verified
        created = await self.repository.add(user)
        return UserPublic.model_validate(created)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self.repository.get_by_email(email)

    async def update_user(self, user_id: UUID, payload: UserUpdate) -> UserPublic:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(user_id, updates)
        if updated is None:
            raise NotFoundError(detail='User not found')
        return UserPublic.model_validate(updated)

    async def confirm_account(self, user_id: UUID) -> UserPublic:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(detail='User not found')
        if user.is_verified:
            raise BadRequestError(detail='Account already confirmed')

        updated = await self.repository.update_fields(user_id, {'is_verified': True})
        if updated is None:
            raise NotFoundError(detail='User not found')
        return UserPublic.model_validate(updated)

    async def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str,
    ) -> None:
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(detail='User not found')

        password_hash = user.password_hash
        if password_hash is None or not Hasher.verify_password(
            current_password,
            password_hash,
        ):
            raise UnauthorizedError(detail='Current password is incorrect')

        await self.repository.update_fields(
            user_id,
            {'password_hash': Hasher.get_password_hash(new_password)},
        )
        await self.refresh_session_service.invalidate_user_sessions(user_id)
