"""Rebuild knowledge fragment embeddings for the configured model.

Run after changing the embedding model or vector size:

    uv run python -m scripts.rebuild_embeddings
"""

import asyncio
import sys

from sqlalchemy import delete
from sqlmodel import select

from src.app.core import settings
from src.app.db.database import AsyncSessionLocal
from src.app.models.embedding import Embedding
from src.app.models.source_fragment import SourceFragment
from src.app.services.local_embedding_service import LocalEmbeddingService


async def main() -> None:
    embedding_service = LocalEmbeddingService()

    async with AsyncSessionLocal() as session:
        await session.execute(
            delete(Embedding).where(
                Embedding.model_name == settings.embeddings.model_name,
            ),
        )
        result = await session.execute(
            select(SourceFragment).order_by(SourceFragment.created_at.asc()),
        )
        fragments = list(result.scalars().all())
        print(
            f'Rebuilding embeddings for {len(fragments)} fragments '
            f'with {settings.embeddings.model_name}',
        )

        for index, fragment in enumerate(fragments, start=1):
            vector = await embedding_service.embed_document(fragment.content)
            if len(vector) != settings.embeddings.dimension:
                msg = (
                    f'Embedding dimension mismatch: got {len(vector)}, '
                    f'expected {settings.embeddings.dimension}'
                )
                raise RuntimeError(msg)

            session.add(
                Embedding(
                    fragment_id=fragment.id,
                    embedding=vector,
                    model_name=settings.embeddings.model_name,
                ),
            )
            print(f'[{index}/{len(fragments)}] {fragment.id}')

        await session.commit()

    print('Embeddings rebuild completed successfully')


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception:
        print('Embeddings rebuild failed', file=sys.stderr)
        raise
