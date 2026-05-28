from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.app.db.database import get_session
from src.app.models.embedding import Embedding
from src.app.models.source import Source
from src.app.models.source_fragment import SourceFragment
from src.app.repositories.base import BaseRepository


class EmbeddingRepository(BaseRepository[Embedding]):
    def __init__(
        self,
        session: Annotated[AsyncSession, Depends(get_session)],
    ):
        super().__init__(session=session, model=Embedding)

    async def list_by_fragment(self, fragment_id: UUID) -> list[Embedding]:
        return await self.get_all(fragment_id=fragment_id)

    async def get_by_fragment_and_model(
        self,
        fragment_id: UUID,
        model_name: str,
    ) -> Embedding | None:
        statement = select(Embedding).where(
            Embedding.fragment_id == fragment_id,
            Embedding.model_name == model_name,
        )
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def search_similar(
        self,
        query_embedding: list[float],
        *,
        model_name: str | None = None,
        limit: int = 5,
        min_similarity: float | None = None,
    ) -> list[tuple[Embedding, float]]:
        distance = Embedding.embedding.cosine_distance(query_embedding)
        similarity = (1 - distance).label('similarity')

        statement = (
            select(Embedding, similarity)
            .join(SourceFragment, Embedding.fragment_id == SourceFragment.id)
            .join(Source, SourceFragment.source_id == Source.id)
            .where(Embedding.embedding.is_not(None))
            .where(SourceFragment.valid_to.is_(None))
            .where(Source.is_active.is_(True))
            .options(selectinload(Embedding.fragment).selectinload(SourceFragment.source))
            .order_by(distance)
            .limit(limit)
        )
        if model_name is not None:
            statement = statement.where(Embedding.model_name == model_name)
        if min_similarity is not None:
            statement = statement.where(similarity >= min_similarity)

        result = await self.session.execute(statement)
        return [(embedding, float(score)) for embedding, score in result.all()]
