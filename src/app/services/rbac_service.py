from __future__ import annotations

from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select

from src.app.core import settings
from src.app.models.rbac_models import Role, UserRoleLink
from src.app.models.user import User


class RbacService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def load_user_with_roles(self, user_id: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.id == user_id)
            .options(
                selectinload(User.rbac_roles).selectinload(Role.permissions),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

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
        stmt = select(Role).where(Role.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def ensure_user_has_role(self, user_id: UUID, role_name: str) -> None:
        role = await self.get_role_by_name(role_name)
        if role is None:
            msg = f"Role '{role_name}' does not exist"
            raise RuntimeError(msg)

        stmt = select(UserRoleLink).where(
            UserRoleLink.user_id == user_id,
            UserRoleLink.role_id == role.id,
        )
        result = await self.session.execute(stmt)
        if result.scalar_one_or_none() is None:
            self.session.add(UserRoleLink(user_id=user_id, role_id=role.id))
            await self.session.commit()

    async def set_user_roles(self, user_id: UUID, role_names: list[str]) -> None:
        roles: list[Role] = []
        for name in role_names:
            role = await self.get_role_by_name(name)
            if role is None:
                msg = f'Unknown role: {name}'
                raise ValueError(msg)
            roles.append(role)

        await self.session.execute(
            delete(UserRoleLink).where(UserRoleLink.user_id == user_id),
        )
        for role in roles:
            self.session.add(UserRoleLink(user_id=user_id, role_id=role.id))
        await self.session.commit()
