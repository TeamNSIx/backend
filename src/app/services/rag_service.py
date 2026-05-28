from time import perf_counter
from typing import Annotated

from fastapi import BackgroundTasks, Depends

from src.app.core import settings
from src.app.models.embedding import Embedding, EmbeddingCreate
from src.app.models.source_fragment import SourceFragmentPublic
from src.app.repositories.embedding_repository import EmbeddingRepository
from src.app.services.llm_service import LLMService
from src.app.services.local_embedding_service import LocalEmbeddingService
from src.app.services.web_ingestion_service import (
    WebChunk,
    WebContext,
    WebIngestionService,
)
from src.utils.logger import logger

NO_CONTEXT_ANSWER = (
    'К сожалению, я не нашел точной информации по вашему вопросу в базе знаний. '
    'Попробуйте переформулировать запрос или обратитесь к модератору.'
)

RAG_SYSTEM_PROMPT = """
Ты помощник для адаптации студентов Казанского федерального университета.
Отвечай на русском языке только на основе переданного контекста из базы знаний.
Если в контексте нет точного ответа, честно скажи, что точной информации нет.
Если студент использует бытовое название, а в контексте есть официальный термин
для того же студенческого запроса, ответь с уточнением официального названия.
Например: если спрашивают про деканат ИТИС, а в контексте есть директорат ИТИС,
ответь, что в источнике указан директорат, и используй данные директората.
Если точного ответа нет, не перечисляй типичные варианты и не делай предположений.
Не придумывай адреса, контакты, сроки, правила и имена преподавателей.
""".strip()

BOILERPLATE_MARKERS_THRESHOLD = 2


class RAGService:
    def __init__(
        self,
        embedding_repository: Annotated[
            EmbeddingRepository,
            Depends(EmbeddingRepository),
        ],
        local_embedding_service: Annotated[
            LocalEmbeddingService,
            Depends(LocalEmbeddingService),
        ],
        llm_service: Annotated[LLMService, Depends(LLMService)],
        web_ingestion_service: Annotated[
            WebIngestionService,
            Depends(WebIngestionService),
        ],
    ) -> None:
        self.embedding_repository = embedding_repository
        self.local_embedding_service = local_embedding_service
        self.llm_service = llm_service
        self.web_ingestion_service = web_ingestion_service

    async def create_fragment_embedding(
        self,
        fragment: SourceFragmentPublic,
    ) -> Embedding:
        vector = await self.local_embedding_service.embed_document(fragment.content)
        existing = await self.embedding_repository.get_by_fragment_and_model(
            fragment.id,
            settings.embeddings.model_name,
        )
        if existing is not None:
            existing.embedding = vector
            existing.model_name = settings.embeddings.model_name
            return await self.embedding_repository.save(existing)

        embedding = Embedding.model_validate(
            EmbeddingCreate(
                fragment_id=fragment.id,
                embedding=vector,
                model_name=settings.embeddings.model_name,
            ),
        )
        return await self.embedding_repository.add(embedding)

    async def generate_answer(
        self,
        question: str,
        background_tasks: BackgroundTasks | None = None,
    ) -> tuple[str, dict]:
        rag_started = perf_counter()
        timings_ms: dict[str, int] = {}

        try:
            embedding_started = perf_counter()
            query_embedding = await self.local_embedding_service.embed_query(question)
            timings_ms['query_embedding'] = self._elapsed_ms(embedding_started)

            search_started = perf_counter()
            matches = await self.embedding_repository.search_similar(
                query_embedding,
                model_name=settings.embeddings.model_name,
                limit=settings.gigachat.rag_top_k,
                min_similarity=settings.gigachat.rag_min_similarity,
            )
            timings_ms['vector_search'] = self._elapsed_ms(search_started)
        except Exception as exc:
            logger.warning('RAG search failed: %s', exc)
            timings_ms['total_rag'] = self._elapsed_ms(rag_started)
            return settings.llm.fallback_answer, {
                'rag_enabled': True,
                'rag_available': False,
                'llm_available': False,
                'reason': str(exc),
                'embedding_model': settings.embeddings.model_name,
                'timings_ms': timings_ms,
            }

        if not matches:
            web_started = perf_counter()
            web_context = await self.web_ingestion_service.find_context(
                query_embedding,
            )
            timings_ms['web_fallback'] = self._elapsed_ms(web_started)
            if web_context is not None:
                answer, metadata = await self._generate_web_answer(
                    question,
                    web_context,
                    timings_ms,
                    rag_started,
                )
                if (
                    settings.web_ingestion.persist_found_context
                    and background_tasks is not None
                ):
                    background_tasks.add_task(
                        WebIngestionService.persist_context_task,
                        web_context,
                    )
                return answer, metadata

            timings_ms['total_rag'] = self._elapsed_ms(rag_started)
            return NO_CONTEXT_ANSWER, {
                'rag_enabled': True,
                'rag_available': True,
                'context_found': False,
                'web_fallback_used': False,
                'embedding_model': settings.embeddings.model_name,
                'used_fragments': [],
                'timings_ms': timings_ms,
            }

        prompt_matches = self._select_prompt_matches(matches)
        filtered_fragments_count = len(matches) - len(prompt_matches)
        prompt = self._build_prompt(question, prompt_matches)
        llm_started = perf_counter()
        answer, llm_metadata = await self.llm_service.generate_answer(
            prompt,
            system_prompt=RAG_SYSTEM_PROMPT,
        )
        timings_ms['llm_generation'] = self._elapsed_ms(llm_started)
        if self._should_try_web_after_llm(answer, llm_metadata):
            web_started = perf_counter()
            web_context = await self.web_ingestion_service.find_context(
                query_embedding,
            )
            timings_ms['web_fallback_after_local_llm'] = self._elapsed_ms(web_started)
            if web_context is not None:
                answer, metadata = await self._generate_web_answer(
                    question,
                    web_context,
                    timings_ms,
                    rag_started,
                    local_matches=prompt_matches,
                )
                self._schedule_web_context_persist(web_context, background_tasks)
                return answer, metadata

        timings_ms['total_rag'] = self._elapsed_ms(rag_started)
        answer, answer_guard_metadata = self._guard_answer(answer, prompt)
        return answer, {
            **llm_metadata,
            'rag_enabled': True,
            'rag_available': True,
            'context_found': True,
            'web_fallback_used': False,
            'embedding_model': settings.embeddings.model_name,
            'used_fragments': [
                self._fragment_metadata(item, score)
                for item, score in prompt_matches
            ],
            'timings_ms': timings_ms,
            **(
                {'filtered_fragments_count': filtered_fragments_count}
                if filtered_fragments_count
                else {}
            ),
            **answer_guard_metadata,
        }

    async def _generate_web_answer(
        self,
        question: str,
        context: WebContext,
        timings_ms: dict[str, int],
        rag_started: float,
        local_matches: list[tuple[Embedding, float]] | None = None,
    ) -> tuple[str, dict]:
        web_chunks = self._select_web_chunks(context.chunks)
        prompt = self._build_web_prompt(
            question,
            context,
            web_chunks,
            local_matches=local_matches,
        )
        llm_started = perf_counter()
        answer, llm_metadata = await self.llm_service.generate_answer(
            prompt,
            system_prompt=RAG_SYSTEM_PROMPT,
        )
        timing_key = (
            'web_llm_generation'
            if 'llm_generation' in timings_ms
            else 'llm_generation'
        )
        timings_ms[timing_key] = self._elapsed_ms(llm_started)
        timings_ms['total_rag'] = self._elapsed_ms(rag_started)
        answer, answer_guard_metadata = self._guard_answer(answer, prompt)
        return answer, {
            **llm_metadata,
            'rag_enabled': True,
            'rag_available': True,
            'context_found': True,
            'web_fallback_used': True,
            'embedding_model': settings.embeddings.model_name,
            'used_fragments': [
                self._fragment_metadata(item, score)
                for item, score in (local_matches or [])
            ],
            'used_web_sources': [
                {
                    'source_url': context.source_url,
                    'source_title': context.source_title,
                    'similarity': round(chunk.similarity, 4),
                }
                for chunk in web_chunks
            ],
            'timings_ms': timings_ms,
            **answer_guard_metadata,
        }

    def _schedule_web_context_persist(
        self,
        context: WebContext,
        background_tasks: BackgroundTasks | None,
    ) -> None:
        if (
            settings.web_ingestion.persist_found_context
            and background_tasks is not None
        ):
            background_tasks.add_task(
                WebIngestionService.persist_context_task,
                context,
            )

    def _should_try_web_after_llm(self, answer: str, llm_metadata: dict) -> bool:
        if not settings.web_ingestion.enabled or not llm_metadata.get('llm_available'):
            return False
        normalized = answer.lower()
        fallback_markers = (
            'точной информации',
            'точного ответа',
            'не нашел',
            'не нашёл',
            'нет в предоставленном контексте',
        )
        return any(marker in normalized for marker in fallback_markers)

    def _is_gigachat_disclaimer(self, answer: str) -> bool:
        normalized = answer.lower()
        return (
            'gigachat не обладает собственным мнением' in normalized
            or 'генеративные языковые модели не обладают собственным мнением'
            in normalized
            or 'разговоры на некоторые темы временно ограничены' in normalized
            or 'разговоры на чувствительные темы могут быть ограничены' in normalized
            or 'иногда генеративные языковые модели могут создавать некорректные ответы'
            in normalized
            or 'ответы на вопросы, связанные с чувствительными темами' in normalized
        )

    def _llm_debug_metadata(self, answer: str, prompt: str) -> dict:
        is_disclaimer = self._is_gigachat_disclaimer(answer)
        metadata = {'llm_answer_disclaimer': is_disclaimer}
        if settings.debug or is_disclaimer:
            metadata['debug_prompt_preview'] = prompt[:4000]
            metadata['debug_system_prompt'] = RAG_SYSTEM_PROMPT
        return metadata

    def _guard_answer(self, answer: str, prompt: str) -> tuple[str, dict]:
        metadata = self._llm_debug_metadata(answer, prompt)
        if not self._is_unsupported_guess(answer):
            return answer, metadata

        metadata['llm_answer_replaced'] = True
        metadata['llm_answer_replacement_reason'] = 'unsupported_guess'
        if settings.debug:
            metadata['llm_original_answer_preview'] = answer[:1000]
        return NO_CONTEXT_ANSWER, metadata

    def _is_unsupported_guess(self, answer: str) -> bool:
        normalized = answer.lower()
        markers = (
            'можно предположить',
            'предположить, что',
            'предположительно',
            'вероятно',
            'скорее всего',
            'стандартные разделы',
            'характерных для',
        )
        return any(marker in normalized for marker in markers)

    def _select_prompt_matches(
        self,
        matches: list[tuple[Embedding, float]],
    ) -> list[tuple[Embedding, float]]:
        clean_matches = [
            match
            for match in matches
            if not self._is_boilerplate_web_fragment(match[0])
        ]
        return clean_matches or matches

    def _is_boilerplate_web_fragment(self, embedding: Embedding) -> bool:
        fragment = embedding.fragment
        source_url = (fragment.source.url or '').lower()
        if not source_url.startswith(('http://', 'https://')):
            return False

        return self._is_boilerplate_web_text(fragment.content)

    def _is_boilerplate_web_text(self, content: str) -> bool:
        text = content.lower()
        markers = (
            'все новости',
            'файлы cookie',
            'версия для слабовидящих',
            'карта сайта',
            'фирменный стиль',
            'аккредитация журналистов',
            'техническая поддержка',
            'обратная связь',
            '© казанский федеральный университет',
            'public.mail@kpfu.ru',
            'продолжая работу с сайтом',
            'россия — исламский мир',
        )
        return (
            sum(marker in text for marker in markers)
            >= BOILERPLATE_MARKERS_THRESHOLD
        )

    def _select_web_chunks(self, chunks: list[WebChunk]) -> list[WebChunk]:
        clean_chunks = [
            chunk
            for chunk in chunks
            if not self._is_boilerplate_web_text(chunk.content)
        ]
        return clean_chunks or chunks

    def _build_prompt(
        self,
        question: str,
        matches: list[tuple[Embedding, float]],
    ) -> str:
        context_parts = []
        for index, (embedding, similarity) in enumerate(matches, start=1):
            fragment = embedding.fragment
            source = fragment.source
            source_title = source.title or source.url
            context_parts.append(
                f'[{index}] Источник: {source_title}\n'
                f'URL: {source.url}\n'
                f'Релевантность: {similarity:.3f}\n'
                f'Текст: {fragment.content}',
            )

        context = '\n\n'.join(context_parts)
        return (
            f'Вопрос студента: {question}\n\n'
            f'Контекст из базы знаний:\n{context}\n\n'
            'Сформулируй ответ студенту. Если используешь факты, опирайся только '
            'на контекст выше. Если вопрос задан бытовым названием, а в контексте '
            'есть официальный термин для того же объекта, явно укажи это. '
            'Если точного ответа нет, не предполагай.'
        )

    def _build_web_prompt(
        self,
        question: str,
        context: WebContext,
        chunks: list[WebChunk],
        local_matches: list[tuple[Embedding, float]] | None = None,
    ) -> str:
        context_parts = []
        for index, (embedding, similarity) in enumerate(
            local_matches or [],
            start=1,
        ):
            fragment = embedding.fragment
            source = fragment.source
            source_title = source.title or source.url
            context_parts.append(
                f'[{index}] Источник: {source_title}\n'
                f'URL: {source.url}\n'
                f'Релевантность: {similarity:.3f}\n'
                f'Текст: {fragment.content}',
            )

        start_index = len(context_parts) + 1
        for index, chunk in enumerate(chunks, start=start_index):
            context_parts.append(
                f'[{index}] Источник: {context.source_title}\n'
                f'URL: {context.source_url}\n'
                f'Релевантность: {chunk.similarity:.3f}\n'
                f'Текст: {chunk.content}',
            )

        web_context = '\n\n'.join(context_parts)
        return (
            f'Вопрос студента: {question}\n\n'
            'Контекст из базы знаний и доверенных веб-источников КФУ:\n'
            f'{web_context}\n\n'
            'Сформулируй ответ студенту. Если используешь факты, опирайся только '
            'на контекст выше. Если вопрос задан бытовым названием, а в контексте '
            'есть официальный термин для того же объекта, явно укажи это. '
            'Если точного ответа нет, не предполагай.'
        )

    def _fragment_metadata(self, embedding: Embedding, similarity: float) -> dict:
        fragment = embedding.fragment
        source = fragment.source
        return {
            'fragment_id': str(fragment.id),
            'source_id': str(source.id),
            'source_title': source.title,
            'source_url': source.url,
            'similarity': round(similarity, 4),
        }

    @staticmethod
    def _elapsed_ms(started_at: float) -> int:
        return round((perf_counter() - started_at) * 1000)
