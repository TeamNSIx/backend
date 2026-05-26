from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import BackgroundTasks, Depends
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from src.app.core import settings
from src.app.db.database import AsyncSessionLocal
from src.app.models.email_notification import (
    EmailNotification,
    EmailNotificationStatus,
    EmailNotificationType,
)
from src.app.repositories.email_notification_repository import (
    EmailNotificationRepository,
)
from src.utils.logger import logger


class EmailService:
    TEMPLATES_DIR = Path(__file__).resolve().parent.parent / 'templates' / 'emails'

    def __init__(
        self,
        repository: Annotated[
            EmailNotificationRepository,
            Depends(EmailNotificationRepository),
        ],
    ) -> None:
        self.repository = repository

    @staticmethod
    def _connection_config() -> ConnectionConfig:
        return ConnectionConfig(
            MAIL_USERNAME=settings.smtp.username,
            MAIL_PASSWORD=settings.smtp.password.get_secret_value(),
            MAIL_FROM=settings.smtp.from_email,
            MAIL_FROM_NAME=settings.smtp.from_name,
            MAIL_PORT=settings.smtp.port,
            MAIL_SERVER=settings.smtp.host,
            MAIL_STARTTLS=settings.smtp.starttls,
            MAIL_SSL_TLS=settings.smtp.ssl_tls,
            USE_CREDENTIALS=settings.smtp.use_credentials,
            TEMPLATE_FOLDER=EmailService.TEMPLATES_DIR,
        )

    @staticmethod
    def _build_fastmail() -> FastMail:
        return FastMail(EmailService._connection_config())

    @staticmethod
    def _confirmation_url(token: str) -> str:
        base = settings.email.frontend_base_url.rstrip('/')
        path = settings.email.confirmation_path
        if not path.startswith('/'):
            path = f'/{path}'
        return f'{base}{path}?token={token}'

    async def schedule_account_confirmation(
        self,
        background_tasks: BackgroundTasks,
        *,
        user_id: UUID,
        recipient: str,
        token: str,
        full_name: str | None = None,
    ) -> EmailNotification:
        confirmation_url = self._confirmation_url(token)
        notification = await self.repository.add(
            EmailNotification(
                user_id=user_id,
                notification_type=EmailNotificationType.ACCOUNT_CONFIRMATION,
                recipient=recipient,
                subject=f'Подтверждение регистрации в {settings.app_name}',
                status=EmailNotificationStatus.PENDING,
            ),
        )
        background_tasks.add_task(
            EmailService.send_notification_task,
            notification.id,
            EmailNotificationType.ACCOUNT_CONFIRMATION,
            recipient,
            confirmation_url,
            full_name,
        )
        return notification

    async def schedule_password_changed_notification(
        self,
        background_tasks: BackgroundTasks,
        *,
        user_id: UUID,
        recipient: str,
        full_name: str | None = None,
    ) -> EmailNotification:
        notification = await self.repository.add(
            EmailNotification(
                user_id=user_id,
                notification_type=EmailNotificationType.PASSWORD_CHANGED,
                recipient=recipient,
                subject=f'Пароль изменён — {settings.app_name}',
                status=EmailNotificationStatus.PENDING,
            ),
        )
        background_tasks.add_task(
            EmailService.send_notification_task,
            notification.id,
            EmailNotificationType.PASSWORD_CHANGED,
            recipient,
            None,
            full_name,
        )
        return notification

    @staticmethod
    async def send_notification_task(
        notification_id: UUID,
        notification_type: EmailNotificationType,
        recipient: str,
        confirmation_url: str | None,
        full_name: str | None,
    ) -> None:
        async with AsyncSessionLocal() as session:
            repository = EmailNotificationRepository(session)
            notification = await repository.get_by_id(notification_id)
            if notification is None:
                logger.error('Email notification %s not found', notification_id)
                return

            if not settings.email.enabled:
                await repository.update_status(
                    notification_id,
                    EmailNotificationStatus.SENT,
                    error_message='Email sending is disabled',
                )
                return

            try:
                fastmail = EmailService._build_fastmail()
                template_body = {
                    'app_name': settings.app_name,
                    'full_name': full_name,
                }

                if notification_type == EmailNotificationType.ACCOUNT_CONFIRMATION:
                    template_body['confirmation_url'] = confirmation_url
                    message = MessageSchema(
                        subject=notification.subject,
                        recipients=[recipient],
                        subtype=MessageType.html,
                        template_body=template_body,
                    )
                    await fastmail.send_message(
                        message,
                        template_name='account_confirmation.html',
                    )
                elif notification_type == EmailNotificationType.PASSWORD_CHANGED:
                    message = MessageSchema(
                        subject=notification.subject,
                        recipients=[recipient],
                        subtype=MessageType.html,
                        template_body=template_body,
                    )
                    await fastmail.send_message(
                        message,
                        template_name='password_changed.html',
                    )

                await repository.update_status(
                    notification_id,
                    EmailNotificationStatus.SENT,
                )
            except Exception as exc:
                logger.exception(
                    'Failed to send email notification %s: %s',
                    notification_id,
                    exc,
                )
                await repository.update_status(
                    notification_id,
                    EmailNotificationStatus.FAILED,
                    error_message=str(exc),
                )
