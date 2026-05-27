from datetime import datetime, timedelta, timezone
from uuid import UUID

from jwt import InvalidTokenError, decode, encode

from src.app.core import settings
from src.utils.error import BadRequestError


class EmailTokenService:
    PURPOSE_ACCOUNT_CONFIRMATION = 'account_confirmation'

    @staticmethod
    def create_account_confirmation_token(user_id: UUID) -> str:
        now = datetime.now(timezone.utc)
        expires_at = now + timedelta(
            seconds=settings.email.confirmation_token_lifetime_seconds,
        )
        payload = {
            'sub': str(user_id),
            'purpose': EmailTokenService.PURPOSE_ACCOUNT_CONFIRMATION,
            'exp': expires_at,
            'iat': now,
        }
        return encode(
            payload=payload,
            key=settings.auth.secret.get_secret_value(),
            algorithm=settings.auth.algorithm,
        )

    @staticmethod
    def verify_account_confirmation_token(token: str) -> UUID:
        try:
            payload = decode(
                jwt=token,
                key=settings.auth.secret.get_secret_value(),
                algorithms=(settings.auth.algorithm,),
            )
        except (InvalidTokenError, ValueError) as exc:
            raise BadRequestError(
                detail='Invalid or expired confirmation token',
            ) from exc

        if payload.get('purpose') != EmailTokenService.PURPOSE_ACCOUNT_CONFIRMATION:
            raise BadRequestError(detail='Invalid confirmation token')

        raw_user_id = payload.get('sub')
        if raw_user_id is None:
            raise BadRequestError(detail='Invalid confirmation token')

        return UUID(raw_user_id)
