from uuid import UUID

from src.app.models.refresh import RefreshSession, RefreshSessionCreate
from src.app.repositories.refresh_session_repository import RefreshSessionRepository


class RefreshSessionService:
    __refresh_session_repository: RefreshSessionRepository

    def __init__(self, refresh_session_repository: RefreshSessionRepository):
        self.__refresh_session_repository = refresh_session_repository

    async def get_active_user_session(self, user_id: UUID) -> RefreshSession | None:
        user_sessions = await self.__refresh_session_repository.list_by_user(user_id)
        if len(user_sessions) == 0:
            return None

        valid_sessions = list(
            filter(
                lambda session: session.is_valid,
                user_sessions
            )
        )

        if len(valid_sessions) != 1:
            return None

        return valid_sessions[0]

    async def has_user_active_session(self, user_id: UUID) -> bool:
        user_active_session = await self.get_active_user_session(user_id)

        return user_active_session is not None

    async def save_session(self, session: RefreshSession) -> RefreshSession:
        return await self.__refresh_session_repository.save(session)

    async def create_session(
        self,
        session_create_data: RefreshSessionCreate,
    ) -> RefreshSession:
        instance = RefreshSession(**session_create_data.model_dump())
        return await self.__refresh_session_repository.save(instance)