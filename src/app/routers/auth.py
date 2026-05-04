from typing import Annotated

from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    HTTPException,
    Response,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from src.app.core import settings
from src.app.dependencies import RbacServiceDep, UserServiceDep
from src.app.dependencies.auth import AuthenticatorDep, get_current_user
from src.app.models.user import UserCreate, UserPublic
from src.app.schemas.auth import AuthData, AuthTokenData, RegisterData, RegisterResponse

router = APIRouter(prefix='/auth', tags=['auth'])

REFRESH_COOKIE_KEY = 'refresh_token'

OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
RefreshCookieDep = Annotated[str | None, Cookie(alias=REFRESH_COOKIE_KEY)]


@router.post(
    '/register',
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register(
    payload: RegisterData,
    user_service: UserServiceDep,
    rbac_service: RbacServiceDep,
):
    user_payload = UserCreate.model_validate(payload.model_dump(exclude={'password'}))
    user = await user_service.create_user_with_password(
        user_payload,
        payload.password.get_secret_value(),
    )
    await rbac_service.ensure_user_has_role(user.id, settings.rbac.public_role_name)
    return RegisterResponse(success=True, user=user)


@router.post('/login', response_model=AuthTokenData)
async def login(
    response: Response,
    authenticator: AuthenticatorDep,
    form_data: OAuth2FormDep,
):
    token_data = await authenticator.create_token(
        AuthData(username=form_data.username, password=form_data.password),
    )
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid credentials',
        )

    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=token_data.refresh_token,
        httponly=True,
        samesite='lax',
    )
    return token_data


@router.get('/me', response_model=UserPublic)
async def me(
    current_user: Annotated[
        UserPublic,
        Security(get_current_user, scopes=['profile:detail']),
    ],
):
    return current_user


@router.post('/logout')
async def logout(
    response: Response,
    authenticator: AuthenticatorDep,
    refresh_token: RefreshCookieDep = None,
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token not provided',
        )

    is_logged_out = await authenticator.logout(refresh_token)
    if not is_logged_out:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Logout failed',
        )

    response.delete_cookie(REFRESH_COOKIE_KEY)
    return {'success': True}


@router.post('/refresh', response_model=AuthTokenData)
async def refresh(
    response: Response,
    authenticator: AuthenticatorDep,
    refresh_token: RefreshCookieDep = None,
):
    if refresh_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Refresh token not provided',
        )

    token_data = await authenticator.refresh_tokens(refresh_token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid refresh token',
        )

    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=token_data.refresh_token,
        httponly=True,
        samesite='lax',
    )
    return token_data
