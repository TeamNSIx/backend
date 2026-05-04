from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID, uuid4

from fastapi import HTTPException, status
from jwt import InvalidTokenError, decode, encode

from src.app.core import settings as config
from src.app.models.refresh import RefreshSessionCreate
from src.app.models.user import UserPublic
from src.app.schemas.auth import AuthData, AuthTokenData, UserTokenData
from src.app.services.rbac_service import RbacService
from src.app.services.refresh import RefreshSessionService
from src.app.services.user_service import UserService
from src.utils.hasher import Hasher


class Authenticator:
    __user_service: UserService
    __refresh_session_service: RefreshSessionService
    __rbac_service: RbacService

    def __init__(
        self,
        user_service: UserService,
        refresh_session_service: RefreshSessionService,
        rbac_service: RbacService,
    ):
        self.__user_service = user_service
        self.__refresh_session_service = refresh_session_service
        self.__rbac_service = rbac_service

    async def create_token(self, auth_data: AuthData) -> Optional[AuthTokenData]:
        user = await self.__user_service.get_user_by_email(auth_data.username)
        if user is None:
            return None

        password_hash = user.password_hash
        if password_hash is None:
            return None
        password = auth_data.password.get_secret_value()
        if not Hasher.verify_password(password, password_hash):
            return None

        return await self.__generate_tokens(user.id)

    async def __generate_tokens(self, user_id: UUID) -> Optional[AuthTokenData]:
        refresh_svc = self.__refresh_session_service
        has_active_sessions = await refresh_svc.has_user_active_session(user_id)
        if has_active_sessions:
            return None

        user_with_roles = await self.__rbac_service.load_user_with_roles(user_id)
        scopes = (
            self.__rbac_service.effective_scopes(user_with_roles)
            if user_with_roles is not None
            else []
        )

        now = datetime.now(timezone.utc)

        access_token_id = uuid4()
        access_token_lifetime = timedelta(
            seconds=config.auth.access_token_lifetime_seconds,
        )
        access_token_expires_at = now + access_token_lifetime
        access_token = self.__create_user_token(
            user_id=user_id,
            token_id=access_token_id,
            expires_at=access_token_expires_at,
            scopes=scopes,
        )

        refresh_token_id = uuid4()
        refresh_token_lifetime = timedelta(
            seconds=config.auth.refresh_token_lifetime_seconds,
        )
        refresh_token_expires_at = now + refresh_token_lifetime
        refresh_token = self.__create_user_token(
            user_id=user_id,
            token_id=refresh_token_id,
            expires_at=refresh_token_expires_at,
        )

        await refresh_svc.create_session(
            RefreshSessionCreate(
                user_id=user_id,
                access_token_id=access_token_id,
                refresh_token_id=refresh_token_id,
                expires_at=refresh_token_expires_at,
            ),
        )

        return AuthTokenData(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def __create_user_token(
        self,
        user_id: UUID,
        token_id: UUID,
        expires_at: datetime,
        *,
        scopes: list[str] | None = None,
    ) -> str:
        now = datetime.now(timezone.utc)
        payload: dict = {
            'sub': str(user_id),
            'exp': expires_at,
            'jti': str(token_id),
            'iat': now,
        }
        if scopes is not None:
            payload['scopes'] = scopes

        return encode(
            payload=payload,
            key=config.auth.secret.get_secret_value(),
            algorithm=config.auth.algorithm,
        )

    async def authenticate_user(
        self,
        access_token: str,
        required_scopes: list[str],
    ) -> UserPublic:
        token_data = self.__get_user_token_data(access_token)
        if token_data is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Unauthorized',
            )

        user_id = UUID(token_data.user_id)
        access_token_id = UUID(token_data.token_id)

        refresh_svc = self.__refresh_session_service
        active_session = await refresh_svc.get_active_user_session(user_id)
        if active_session is None or active_session.access_token_id != access_token_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Unauthorized',
            )

        user = await self.__rbac_service.load_user_with_roles(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Unauthorized',
            )

        effective = self.__rbac_service.effective_scopes(user)
        if not self.__rbac_service.scopes_allow(effective, required_scopes):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='Forbidden',
            )

        return UserPublic.model_validate(user)

    async def logout(self, token: str) -> bool:
        token_data = self.__get_user_token_data(token)
        if token_data is None:
            return False

        user_id = UUID(token_data.user_id)
        token_id = UUID(token_data.token_id)
        refresh_svc = self.__refresh_session_service
        user_active_session = await refresh_svc.get_active_user_session(user_id)
        if user_active_session is None:
            return False
        allowed = {
            user_active_session.access_token_id,
            user_active_session.refresh_token_id,
        }
        if token_id not in allowed:
            return False

        user_active_session.is_invalidated = True
        await refresh_svc.save_session(user_active_session)
        return True

    async def refresh_tokens(self, refresh_token: str) -> Optional[AuthTokenData]:
        token_data = self.__get_user_token_data(refresh_token)
        if token_data is None:
            return None

        user_id = UUID(token_data.user_id)
        refresh_token_id = UUID(token_data.token_id)
        refresh_svc = self.__refresh_session_service
        user_active_session = await refresh_svc.get_active_user_session(user_id)
        if user_active_session is None:
            return None
        if user_active_session.refresh_token_id != refresh_token_id:
            return None

        user_active_session.is_invalidated = True
        await refresh_svc.save_session(user_active_session)
        return await self.__generate_tokens(user_id)

    def __get_user_token_data(self, token: str) -> Optional[UserTokenData]:
        try:
            decoded_payload = decode(
                jwt=token,
                key=config.auth.secret.get_secret_value(),
                algorithms=(config.auth.algorithm,),
            )
        except (InvalidTokenError, ValueError):
            return None

        raw_user_id = decoded_payload.get('sub')
        raw_token_id = decoded_payload.get('jti')
        if raw_user_id is None or raw_token_id is None:
            return None

        return UserTokenData(
            user_id=raw_user_id,
            token_id=raw_token_id,
        )
