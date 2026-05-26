from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Cookie,
    Depends,
    Request,
    Response,
    Security,
    status,
)
from fastapi.security import OAuth2PasswordRequestForm

from src.app.core import settings
from src.app.core.rate_limit import limiter
from src.app.core.responses import (
    auth_responses,
    bad_request_responses,
    common_responses,
    conflict_responses,
    detail_responses,
    merge_responses,
)
from src.app.dependencies import EmailServiceDep, RbacServiceDep, UserServiceDep
from src.app.dependencies.auth import AuthenticatorDep, get_current_user
from src.app.models.user import UserCreate, UserPublic
from src.app.schemas.auth import (
    AuthData,
    AuthTokenData,
    ChangePasswordData,
    ConfirmAccountData,
    RegisterData,
    RegisterResponse,
    SuccessResponse,
)
from src.app.services.email_token_service import EmailTokenService
from src.utils.error import ConflictError, UnauthorizedError

router = APIRouter(prefix='/auth', tags=['auth'])

REFRESH_COOKIE_KEY = 'refresh_token'

OAuth2FormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
RefreshCookieDep = Annotated[str | None, Cookie(alias=REFRESH_COOKIE_KEY)]

_auth_responses = merge_responses(common_responses, auth_responses)
_register_responses = merge_responses(_auth_responses, conflict_responses)
_token_responses = merge_responses(_auth_responses, bad_request_responses)
_confirm_responses = merge_responses(
    common_responses,
    bad_request_responses,
    detail_responses,
)
_change_password_responses = merge_responses(_auth_responses, bad_request_responses)


@router.post(
    '/register',
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses=_register_responses,
)
@limiter.limit(settings.rate_limit.auth)
async def register(
    request: Request,  # noqa: ARG001
    payload: RegisterData,
    background_tasks: BackgroundTasks,
    user_service: UserServiceDep,
    rbac_service: RbacServiceDep,
    email_service: EmailServiceDep,
):
    existing_user = await user_service.get_user_by_email(payload.email)
    if existing_user is not None:
        raise ConflictError(detail='User with this email already exists')

    user_payload = UserCreate.model_validate(payload.model_dump(exclude={'password'}))
    user = await user_service.create_user_with_password(
        user_payload,
        payload.password.get_secret_value(),
        is_verified=False,
    )
    await rbac_service.ensure_user_has_role(user.id, settings.rbac.public_role_name)

    confirmation_token = EmailTokenService.create_account_confirmation_token(user.id)
    await email_service.schedule_account_confirmation(
        background_tasks,
        user_id=user.id,
        recipient=str(payload.email),
        token=confirmation_token,
        full_name=payload.full_name,
    )

    return RegisterResponse(
        success=True,
        user=user,
        message='Registration successful. Please confirm your email.',
    )


@router.post(
    '/confirm',
    response_model=SuccessResponse,
    responses=_confirm_responses,
)
@limiter.limit(settings.rate_limit.auth)
async def confirm_account(
    request: Request,  # noqa: ARG001
    payload: ConfirmAccountData,
    user_service: UserServiceDep,
):
    user_id = EmailTokenService.verify_account_confirmation_token(payload.token)
    await user_service.confirm_account(user_id)
    return SuccessResponse(message='Account confirmed successfully')


@router.post('/login', response_model=AuthTokenData, responses=_token_responses)
@limiter.limit(settings.rate_limit.auth)
async def login(
    request: Request,  # noqa: ARG001
    response: Response,
    authenticator: AuthenticatorDep,
    form_data: OAuth2FormDep,
):
    token_data = await authenticator.create_token(
        AuthData(username=form_data.username, password=form_data.password),
    )
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=token_data.refresh_token,
        httponly=True,
        samesite='lax',
    )
    return token_data


@router.get('/me', response_model=UserPublic, responses=_auth_responses)
async def me(
    current_user: Annotated[
        UserPublic,
        Security(get_current_user, scopes=['profile:detail']),
    ],
):
    return current_user


@router.post(
    '/change-password',
    response_model=SuccessResponse,
    responses=_change_password_responses,
)
async def change_password(
    payload: ChangePasswordData,
    background_tasks: BackgroundTasks,
    current_user: Annotated[
        UserPublic,
        Security(get_current_user, scopes=['profile:detail']),
    ],
    user_service: UserServiceDep,
    email_service: EmailServiceDep,
):
    await user_service.change_password(
        current_user.id,
        payload.current_password.get_secret_value(),
        payload.new_password.get_secret_value(),
    )

    if current_user.email is not None:
        await email_service.schedule_password_changed_notification(
            background_tasks,
            user_id=current_user.id,
            recipient=current_user.email,
            full_name=current_user.full_name,
        )

    return SuccessResponse(message='Password changed successfully')


@router.post('/logout', responses=_token_responses)
async def logout(
    response: Response,
    authenticator: AuthenticatorDep,
    refresh_token: RefreshCookieDep = None,
):
    if refresh_token is None:
        raise UnauthorizedError(detail='Refresh token not provided')

    await authenticator.logout(refresh_token)
    response.delete_cookie(REFRESH_COOKIE_KEY)
    return SuccessResponse(message='Logged out successfully')


@router.post('/refresh', response_model=AuthTokenData, responses=_token_responses)
@limiter.limit(settings.rate_limit.auth)
async def refresh(
    request: Request,  # noqa: ARG001
    response: Response,
    authenticator: AuthenticatorDep,
    refresh_token: RefreshCookieDep = None,
):
    if refresh_token is None:
        raise UnauthorizedError(detail='Refresh token not provided')

    token_data = await authenticator.refresh_tokens(refresh_token)
    response.set_cookie(
        key=REFRESH_COOKIE_KEY,
        value=token_data.refresh_token,
        httponly=True,
        samesite='lax',
    )
    return token_data
