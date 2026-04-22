from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from src.app.dependencies import UserServiceDep
from src.app.models.user import UserCreate, UserPublic, UserUpdate

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=list[UserPublic])
async def list_users(service: UserServiceDep):
    return await service.list_users()


@router.get('/{user_id}', response_model=UserPublic)
async def get_user(user_id: UUID, service: UserServiceDep):
    user = await service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user


@router.post('/', response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, service: UserServiceDep):
    return await service.create_user(payload)


@router.patch('/{user_id}', response_model=UserPublic)
async def update_user(user_id: UUID, payload: UserUpdate, service: UserServiceDep):
    user = await service.update_user(user_id, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')
    return user
