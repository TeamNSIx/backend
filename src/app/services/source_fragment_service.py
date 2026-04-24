from uuid import UUID

from src.app.models.source_fragment import (
    SourceFragment,
    SourceFragmentCreate,
    SourceFragmentPublic,
    SourceFragmentUpdate,
)
from src.app.repositories.source_fragment_repository import SourceFragmentRepository


class SourceFragmentService:
    def __init__(self, repository: SourceFragmentRepository) -> None:
        self.repository = repository

    async def list_fragments(self, source_id: UUID | None = None) -> list[SourceFragmentPublic]:
        if source_id is None:
            fragments = await self.repository.get_all()
        else:
            fragments = await self.repository.list_by_source(source_id)
        return [SourceFragmentPublic.model_validate(fragment) for fragment in fragments]

    async def get_fragment(self, fragment_id: UUID) -> SourceFragmentPublic | None:
        fragment = await self.repository.get_by_id(fragment_id)
        if fragment is None:
            return None
        return SourceFragmentPublic.model_validate(fragment)

    async def create_fragment(self, payload: SourceFragmentCreate) -> SourceFragmentPublic:
        fragment = SourceFragment.model_validate(payload)
        created = await self.repository.add(fragment)
        return SourceFragmentPublic.model_validate(created)

    async def update_fragment(
        self,
        fragment_id: UUID,
        payload: SourceFragmentUpdate,
    ) -> SourceFragmentPublic | None:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(fragment_id, updates)
        if updated is None:
            return None
        return SourceFragmentPublic.model_validate(updated)
