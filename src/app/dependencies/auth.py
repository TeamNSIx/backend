from typing import Annotated

from fastapi import Depends
from fastapi.security import SecurityScopes

from src.app.core.auth import Authenticator
from src.app.core.security import AccessTokenDep
from src.app.dependencies import (
    RbacServiceDep,
    RefreshSessionServiceDep,
    UserServiceDep,
)
from src.app.models.user import UserPublic


def get_authenticator(
    user_service: UserServiceDep,
    refresh_session_service: RefreshSessionServiceDep,
    rbac_service: RbacServiceDep,
) -> Authenticator:
    return Authenticator(user_service, refresh_session_service, rbac_service)


AuthenticatorDep = Annotated[Authenticator, Depends(get_authenticator)]


async def get_current_user(
    security_scopes: SecurityScopes,
    authenticator: AuthenticatorDep,
    access_token: AccessTokenDep,
) -> UserPublic:
    return await authenticator.authenticate_user(access_token, security_scopes.scopes)
