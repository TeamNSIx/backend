from typing import Annotated

from fastapi import Depends
from fastapi.security import SecurityScopes

from src.app.core.auth import Authenticator
from src.app.core.security import AccessTokenDep
from src.app.models.user import UserPublic

AuthenticatorDep = Annotated[Authenticator, Depends(Authenticator)]


async def get_current_user(
    security_scopes: SecurityScopes,
    authenticator: AuthenticatorDep,
    access_token: AccessTokenDep,
) -> UserPublic:
    return await authenticator.authenticate_user(access_token, security_scopes.scopes)
