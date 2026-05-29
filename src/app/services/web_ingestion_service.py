from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated
from urllib.parse import urlparse

import httpx
from fastapi import Depends

from src.app.core import settings
from src.app.db.database import AsyncSessionLocal
from src.app.models.embedding import Embedding
from src.app.models.source import Source, SourceType
from src.app.models.source_fragment import SourceFragment
from src.app.repositories.source_fragment_repository import SourceFragmentRepository
from src.app.repositories.source_repository import SourceRepository
from src.app.services.local_embedding_service import LocalEmbeddingService
from src.app.services.web_text_extractor import (
    extract_web_text,
    split_text_into_chunks,
)


@dataclass
class WebChunk:
    content: str
    similarity: float
    embedding: list[float]


@dataclass
class WebContext:
    source_url: str
    source_title: str
    content_hash: str
    chunks: list[WebChunk]


class WebIngestionService:
    def __init__(
        self,
        source_repository: Annotated[SourceRepository, Depends(SourceRepository)],
        fragment_repository: Annotated[
            SourceFragmentRepository,
            Depends(SourceFragmentRepository),
        ],
        local_embedding_service: Annotated[
            LocalEmbeddingService,
            Depends(LocalEmbeddingService),
        ],
    ) -> None:
        self.source_repository = source_repository
        self.fragment_repository = fragment_repository
        self.local_embedding_service = local_embedding_service

    async def find_context(
        self,
        query_embedding: list[float],
        urls: list[str] | None = None,
    ) -> WebContext | None:
        if not settings.web_ingestion.enabled:
            return None

        contexts: list[WebContext] = []
        candidate_urls = (urls or settings.web_ingestion.fallback_urls_list)[
            : settings.web_ingestion.max_pages_per_request
        ]
        for url in candidate_urls:
            if not self._is_trusted_url(url):
                continue
            page = await self._fetch_page(url)
            if page is None:
                continue

            title, text = page
            chunks = await self._rank_chunks(text, query_embedding)
            if not chunks:
                continue
            contexts.append(
                WebContext(
                    source_url=url,
                    source_title=title or url,
                    content_hash=self._content_hash(text),
                    chunks=chunks,
                ),
            )

        if not contexts:
            return None

        return max(contexts, key=lambda item: item.chunks[0].similarity)

    async def ingest_url(self, url: str, title: str | None = None) -> WebContext:
        if not self._is_trusted_url(url):
            msg = 'URL is not in trusted domains'
            raise ValueError(msg)

        page = await self._fetch_page(url)
        if page is None:
            msg = 'Failed to fetch URL'
            raise ValueError(msg)

        page_title, text = page
        chunks = []
        for chunk in self._split_text(text):
            embedding = await self.local_embedding_service.embed_document(chunk)
            chunks.append(WebChunk(content=chunk, similarity=1.0, embedding=embedding))

        context = WebContext(
            source_url=url,
            source_title=title or page_title or url,
            content_hash=self._content_hash(text),
            chunks=chunks,
        )
        await self.persist_context(context)
        return context

    async def persist_context(self, context: WebContext) -> None:
        source = await self.source_repository.get_by_url(context.source_url)
        now = datetime.now()
        if source is None:
            source = Source(
                url=context.source_url,
                title=context.source_title,
                source_type=SourceType.WEBSITE,
                crawl_config={'content_hash': context.content_hash},
                last_crawled_at=now,
            )
            self.source_repository.session.add(source)
            await self.source_repository.session.flush()
        else:
            old_hash = (source.crawl_config or {}).get('content_hash')
            source.title = context.source_title
            source.last_crawled_at = now
            if old_hash == context.content_hash:
                await self.source_repository.session.commit()
                return
            await self.fragment_repository.expire_active_by_source(source.id)
            source.crawl_config = {'content_hash': context.content_hash}

        for index, chunk in enumerate(context.chunks, start=1):
            fragment = SourceFragment(
                source_id=source.id,
                content=chunk.content,
                chunk_index=index,
                valid_from=now,
            )
            self.source_repository.session.add(fragment)
            await self.source_repository.session.flush()
            self.source_repository.session.add(
                Embedding(
                    fragment_id=fragment.id,
                    embedding=chunk.embedding,
                    model_name=settings.embeddings.model_name,
                ),
            )

        await self.source_repository.session.commit()

    async def _fetch_page(self, url: str) -> tuple[str | None, str] | None:
        try:
            async with httpx.AsyncClient(
                timeout=settings.web_ingestion.timeout_seconds,
                follow_redirects=True,
                verify=settings.gigachat.verify_ssl,
            ) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError:
            return None

        extracted = extract_web_text(response.text)
        if extracted is None:
            return None
        return extracted.title, extracted.text

    async def _rank_chunks(
        self,
        text: str,
        query_embedding: list[float],
    ) -> list[WebChunk]:
        ranked: list[WebChunk] = []
        for chunk in self._split_text(text):
            embedding = await self.local_embedding_service.embed_document(chunk)
            similarity = _cosine_similarity(query_embedding, embedding)
            if similarity >= settings.web_ingestion.min_similarity:
                ranked.append(
                    WebChunk(
                        content=chunk,
                        similarity=similarity,
                        embedding=embedding,
                    ),
                )

        ranked.sort(key=lambda item: item.similarity, reverse=True)
        return ranked[: settings.web_ingestion.max_context_chunks]

    def _split_text(self, text: str) -> list[str]:
        return split_text_into_chunks(
            text,
            chunk_size=settings.web_ingestion.chunk_size,
            chunk_overlap=settings.web_ingestion.chunk_overlap,
        )

    def _is_trusted_url(self, url: str) -> bool:
        host = urlparse(url).hostname
        if host is None:
            return False
        host = host.lower()
        return any(
            host == domain or host.endswith(f'.{domain}')
            for domain in settings.web_ingestion.trusted_domains_list
        )

    def _content_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    @staticmethod
    async def persist_context_task(context: WebContext) -> None:
        async with AsyncSessionLocal() as session:
            service = WebIngestionService(
                SourceRepository(session),
                SourceFragmentRepository(session),
                LocalEmbeddingService(),
            )
            await service.persist_context(context)


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=False))
    left_norm = math.sqrt(sum(item * item for item in left))
    right_norm = math.sqrt(sum(item * item for item in right))
    if not left_norm or not right_norm:
        return 0.0
    return numerator / (left_norm * right_norm)
