from enum import Enum
from uuid import UUID

from sqlmodel import Field, SQLModel

from src.app.models.base_model import BaseModel


class EmailNotificationType(str, Enum):
    ACCOUNT_CONFIRMATION = 'account_confirmation'
    PASSWORD_CHANGED = 'password_changed'


class EmailNotificationStatus(str, Enum):
    PENDING = 'pending'
    SENT = 'sent'
    FAILED = 'failed'


class EmailNotificationBase(SQLModel):
    user_id: UUID | None = Field(default=None, foreign_key='users.id', index=True)
    notification_type: EmailNotificationType
    recipient: str = Field(index=True)
    subject: str
    status: EmailNotificationStatus = Field(
        default=EmailNotificationStatus.PENDING,
        index=True,
    )
    error_message: str | None = None


class EmailNotification(EmailNotificationBase, BaseModel, table=True):
    __tablename__ = 'email_notifications'


class EmailNotificationCreate(EmailNotificationBase):
    pass


class EmailNotificationPublic(EmailNotificationBase, BaseModel):
    pass
