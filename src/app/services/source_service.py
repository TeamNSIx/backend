from uuid import UUID

from src.app.models.source import Source, SourceCreate, SourcePublic, SourceUpdate
from src.app.repositories.source_repository import SourceRepository


class SourceService:
    def __init__(self, repository: SourceRepository) -> None:
        self.repository = repository

    async def list_sources(self) -> list[SourcePublic]:
        sources = await self.repository.get_all()
        return [SourcePublic.model_validate(source) for source in sources]

    async def get_source(self, source_id: UUID) -> SourcePublic | None:
        source = await self.repository.get_by_id(source_id)
        if source is None:
            return None
        return SourcePublic.model_validate(source)

    async def create_source(self, payload: SourceCreate) -> SourcePublic:
        source = Source.model_validate(payload)
        created = await self.repository.add(source)
        return SourcePublic.model_validate(created)

    async def update_source(self, source_id: UUID, payload: SourceUpdate) -> SourcePublic | None:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(source_id, updates)
        if updated is None:
            return None
        return SourcePublic.model_validate(updated)
