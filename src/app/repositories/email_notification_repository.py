from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.db.database import get_session
from src.app.models.email_notification import (
    EmailNotification,
    EmailNotificationStatus,
)
from src.app.repositories.base import BaseRepository


class EmailNotificationRepository(BaseRepository[EmailNotification]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=EmailNotification)

    async def update_status(
        self,
        notification_id: UUID,
        status: EmailNotificationStatus,
        error_message: str | None = None,
    ) -> EmailNotification | None:
        updates: dict = {'status': status}
        if error_message is not None:
            updates['error_message'] = error_message
        return await self.update_fields(notification_id, updates)
