from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from src.app.core import settings
from src.app.core.rbac import ALL_SCOPES, PUBLIC_ROLE_SCOPES
from src.app.models.rbac_models import (
    Permission,
    Role,
    RolePermissionLink,
    UserRoleLink,
)
from src.app.models.user import User
from src.utils.hasher import Hasher


async def run_bootstrap(session: AsyncSession) -> None:
    perm_by_scope: dict[str, Permission] = {}
    for scope in ALL_SCOPES:
        if scope == 'roles:assign':
            subject, action = 'roles', 'assign'
        else:
            subject, action = scope.split(':', maxsplit=1)
        perm_by_scope[scope] = await _get_or_create_permission(session, subject, action)

    admin_role = await _ensure_role(session, settings.rbac.admin_role_name)
    public_role = await _ensure_role(session, settings.rbac.public_role_name)

    admin_permissions = list(perm_by_scope.values())
    await _ensure_role_has_permissions(session, admin_role, admin_permissions)

    public_perms = [perm_by_scope[s] for s in PUBLIC_ROLE_SCOPES]
    await _ensure_role_has_permissions(session, public_role, public_perms)

    await _ensure_admin_user(session, admin_role)

    await session.commit()


async def _get_or_create_permission(
    session: AsyncSession,
    subject: str,
    action: str,
) -> Permission:
    stmt = select(Permission).where(
        Permission.subject == subject,
        Permission.action == action,
    )
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    perm = Permission(subject=subject, action=action)
    session.add(perm)
    await session.flush()
    return perm


async def _ensure_role(session: AsyncSession, name: str) -> Role:
    stmt = select(Role).where(Role.name == name)
    result = await session.execute(stmt)
    existing = result.scalar_one_or_none()
    if existing:
        return existing
    role = Role(name=name)
    session.add(role)
    await session.flush()
    return role


async def _ensure_role_has_permissions(
    session: AsyncSession,
    role: Role,
    permissions: list[Permission],
) -> None:
    for perm in permissions:
        stmt = select(RolePermissionLink).where(
            RolePermissionLink.role_id == role.id,
            RolePermissionLink.permission_id == perm.id,
        )
        res = await session.execute(stmt)
        if res.scalar_one_or_none() is None:
            session.add(RolePermissionLink(role_id=role.id, permission_id=perm.id))
    await session.flush()


async def _ensure_admin_user(session: AsyncSession, admin_role: Role) -> None:
    admin_email = str(settings.rbac.admin_email)
    stmt = select(User).where(User.email == admin_email)
    result = await session.execute(stmt)
    admin_user = result.scalar_one_or_none()

    plain_password = settings.rbac.admin_password.get_secret_value()

    if admin_user is None:
        admin_user = User(
            email=admin_email,
            password_hash=Hasher.get_password_hash(plain_password),
        )
        session.add(admin_user)
        await session.flush()
    elif admin_user.password_hash is None:
        admin_user.password_hash = Hasher.get_password_hash(plain_password)

    stmt_link = select(UserRoleLink).where(
        UserRoleLink.user_id == admin_user.id,
        UserRoleLink.role_id == admin_role.id,
    )
    link_result = await session.execute(stmt_link)
    if link_result.scalar_one_or_none() is None:
        session.add(UserRoleLink(user_id=admin_user.id, role_id=admin_role.id))
        await session.flush()
