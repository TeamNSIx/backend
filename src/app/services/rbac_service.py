from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends

from src.app.core import settings
from src.app.models.rbac_models import Role
from src.app.models.user import User
from src.app.repositories.role_repository import RoleRepository
from src.app.repositories.user_repository import UserRepository
from src.app.repositories.user_role_link_repository import UserRoleLinkRepository


class RbacService:
    def __init__(
        self,
        role_repository: Annotated[RoleRepository, Depends(RoleRepository)],
        user_repository: Annotated[UserRepository, Depends(UserRepository)],
        user_role_link_repository: Annotated[
            UserRoleLinkRepository,
            Depends(UserRoleLinkRepository),
        ],
    ) -> None:
        self.role_repository = role_repository
        self.user_repository = user_repository
        self.user_role_link_repository = user_role_link_repository

    async def load_user_with_roles(self, user_id: UUID) -> User | None:
        return await self.user_repository.get_with_roles(user_id)

    def effective_scopes(self, user: User) -> list[str]:
        names = {r.name for r in user.rbac_roles}
        if settings.rbac.admin_role_name in names:
            return ['*']
        scopes: set[str] = set()
        for role in user.rbac_roles:
            for perm in role.permissions:
                scopes.add(perm.scope)
        return sorted(scopes)

    def scopes_allow(self, effective: list[str], required: list[str]) -> bool:
        if not required:
            return True
        if '*' in effective:
            return True
        return all(scope in effective for scope in required)

    async def get_role_by_name(self, name: str) -> Role | None:
        return await self.role_repository.get_by_name(name)

    async def ensure_user_has_role(self, user_id: UUID, role_name: str) -> None:
        role = await self.get_role_by_name(role_name)
        if role is None:
            msg = f"Role '{role_name}' does not exist"
            raise RuntimeError(msg)

        link = await self.user_role_link_repository.get_link(user_id, role.id)
        if link is None:
            await self.user_role_link_repository.add_link(user_id, role.id)

    async def set_user_roles(self, user_id: UUID, role_names: list[str]) -> None:
        roles: list[Role] = []
        for name in role_names:
            role = await self.get_role_by_name(name)
            if role is None:
                msg = f'Unknown role: {name}'
                raise ValueError(msg)
            roles.append(role)

        role_ids = [role.id for role in roles]
        await self.user_role_link_repository.replace_user_roles(user_id, role_ids)
