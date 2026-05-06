from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, HTTPException, Security, status
from pydantic import BaseModel, Field

from src.app.dependencies import RbacServiceDep, UserServiceDep
from src.app.dependencies.auth import get_current_user
from src.app.models.user import UserCreate, UserPublic, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])

ProfileListAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['profile:list']),
]
ProfileCreateAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['profile:create']),
]
RolesAssignAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['roles:assign']),
]
ProfileDetailAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['profile:detail']),
]
ProfileUpdateAuth = Annotated[
    UserPublic,
    Security(get_current_user, scopes=['profile:update']),
]

_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND,
    detail='User not found',
)


class UserRolesUpdate(BaseModel):
    role_names: list[str] = Field(default_factory=list)


@router.get('/', response_model=list[UserPublic])
async def list_users(
    _: ProfileListAuth,
    service: UserServiceDep,
):
    return await service.list_users()


@router.post('/', response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreate,
    _: ProfileCreateAuth,
    service: UserServiceDep,
):
    return await service.create_user(payload)


@router.patch('/{user_id}/roles', response_model=UserPublic)
async def update_user_roles(
    user_id: UUID,
    payload: UserRolesUpdate,
    rbac_service: RbacServiceDep,
    user_service: UserServiceDep,
    _: RolesAssignAuth,
):
    try:
        await rbac_service.set_user_roles(user_id, payload.role_names)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    user = await user_service.get_user(user_id)
    if user is None:
        raise _NOT_FOUND
    return user


@router.get('/{user_id}', response_model=UserPublic)
async def get_user(
    user_id: UUID,
    _: ProfileDetailAuth,
    service: UserServiceDep,
):
    user = await service.get_user(user_id)
    if user is None:
        raise _NOT_FOUND
    return user


@router.patch('/{user_id}', response_model=UserPublic)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    _: ProfileUpdateAuth,
    service: UserServiceDep,
):
    user = await service.update_user(user_id, payload)
    if user is None:
        raise _NOT_FOUND
    return user
