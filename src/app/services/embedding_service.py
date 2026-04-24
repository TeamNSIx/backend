from uuid import UUID

from src.app.models.embedding import Embedding, EmbeddingCreate, EmbeddingPublic, EmbeddingUpdate
from src.app.repositories.embedding_repository import EmbeddingRepository


class EmbeddingService:
    def __init__(self, repository: EmbeddingRepository) -> None:
        self.repository = repository

    async def list_embeddings(self, fragment_id: UUID | None = None) -> list[EmbeddingPublic]:
        if fragment_id is None:
            embeddings = await self.repository.get_all()
        else:
            embeddings = await self.repository.list_by_fragment(fragment_id)
        return [EmbeddingPublic.model_validate(embedding) for embedding in embeddings]

    async def get_embedding(self, embedding_id: UUID) -> EmbeddingPublic | None:
        embedding = await self.repository.get_by_id(embedding_id)
        if embedding is None:
            return None
        return EmbeddingPublic.model_validate(embedding)

    async def create_embedding(self, payload: EmbeddingCreate) -> EmbeddingPublic:
        embedding = Embedding.model_validate(payload)
        created = await self.repository.add(embedding)
        return EmbeddingPublic.model_validate(created)

    async def update_embedding(
        self,
        embedding_id: UUID,
        payload: EmbeddingUpdate,
    ) -> EmbeddingPublic | None:
        updates = payload.model_dump(exclude_unset=True)
        updated = await self.repository.update_fields(embedding_id, updates)
        if updated is None:
            return None
        return EmbeddingPublic.model_validate(updated)
