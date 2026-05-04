from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel

from src.app.models.base_model import BaseModel

if TYPE_CHECKING:
    from src.app.models.user import User


class RolePermissionLink(SQLModel, table=True):
    __tablename__ = 'role_permission_link'

    role_id: UUID = Field(foreign_key='roles.id', primary_key=True)
    permission_id: UUID = Field(foreign_key='permissions.id', primary_key=True)


class UserRoleLink(SQLModel, table=True):
    __tablename__ = 'user_role_link'

    user_id: UUID = Field(foreign_key='users.id', primary_key=True)
    role_id: UUID = Field(foreign_key='roles.id', primary_key=True)


class Permission(BaseModel, table=True):
    __tablename__ = 'permissions'
    __table_args__ = (
        UniqueConstraint(
            'subject',
            'action',
            name='uq_permission_subject_action',
        ),
    )

    subject: str = Field(index=True)
    action: str = Field(index=True)

    roles: list['Role'] = Relationship(
        back_populates='permissions',
        link_model=RolePermissionLink,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    @property
    def scope(self) -> str:
        return f'{self.subject}:{self.action}'


class Role(BaseModel, table=True):
    __tablename__ = 'roles'

    name: str = Field(unique=True, index=True)

    permissions: list[Permission] = Relationship(
        back_populates='roles',
        link_model=RolePermissionLink,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )

    users: list['User'] = Relationship(
        back_populates='rbac_roles',
        link_model=UserRoleLink,
        sa_relationship_kwargs={'lazy': 'selectin'},
    )
