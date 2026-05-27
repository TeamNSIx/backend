from enum import Enum
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy import Enum as SAEnum
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
    notification_type: EmailNotificationType = Field(
        sa_column=Column(
            SAEnum(EmailNotificationType, native_enum=False, length=64),
            nullable=False,
        ),
    )
    recipient: str = Field(index=True)
    subject: str
    status: EmailNotificationStatus = Field(
        default=EmailNotificationStatus.PENDING,
        sa_column=Column(
            SAEnum(EmailNotificationStatus, native_enum=False, length=32),
            nullable=False,
            index=True,
        ),
    )
    error_message: str | None = None


class EmailNotification(EmailNotificationBase, BaseModel, table=True):
    __tablename__ = 'email_notifications'


class EmailNotificationCreate(EmailNotificationBase):
    pass


class EmailNotificationPublic(EmailNotificationBase, BaseModel):
    pass
