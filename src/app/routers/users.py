from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Request, Security, status
from pydantic import BaseModel, Field

from src.app.core.responses import (
    auth_responses,
    bad_request_responses,
    common_responses,
    detail_responses,
    merge_responses,
)
from src.app.dependencies import RbacServiceDep, UserServiceDep
from src.app.dependencies.auth import get_current_user
from src.app.dependencies.pagination import PaginationDep
from src.app.models.user import UserCreate, UserPublic, UserUpdate
from src.app.schemas.pagination import PaginatedResponse
from src.utils.error import BadRequestError

router = APIRouter(prefix='/users', tags=['users'])

_responses = merge_responses(
    common_responses,
    auth_responses,
    detail_responses,
    bad_request_responses,
)

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


class UserRolesUpdate(BaseModel):
    role_names: list[str] = Field(default_factory=list)


@router.get('/', response_model=PaginatedResponse[UserPublic], responses=_responses)
async def list_users(
    request: Request,
    _: ProfileListAuth,
    service: UserServiceDep,
    pagination: PaginationDep,
):
    _ = request
    return await service.list_users(pagination)


@router.post(
    '/',
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED,
    responses=_responses,
)
async def create_user(
    payload: UserCreate,
    _: ProfileCreateAuth,
    service: UserServiceDep,
):
    return await service.create_user(payload)


@router.patch('/{user_id}/roles', response_model=UserPublic, responses=_responses)
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
        raise BadRequestError(detail=str(exc)) from exc

    return await user_service.get_user(user_id)


@router.get('/{user_id}', response_model=UserPublic, responses=_responses)
async def get_user(
    user_id: UUID,
    _: ProfileDetailAuth,
    service: UserServiceDep,
):
    return await service.get_user(user_id)


@router.patch('/{user_id}', response_model=UserPublic, responses=_responses)
async def update_user(
    user_id: UUID,
    payload: UserUpdate,
    _: ProfileUpdateAuth,
    service: UserServiceDep,
):
    return await service.update_user(user_id, payload)
