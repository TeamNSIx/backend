from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.app.core.rbac import PERMISSION_DESCRIPTIONS

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl='/api/v1/auth/login',
    scopes=PERMISSION_DESCRIPTIONS,
)

AccessTokenDep = Annotated[str, Depends(oauth2_scheme)]
