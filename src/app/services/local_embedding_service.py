import asyncio

from src.app.core import settings


class LocalEmbeddingService:
    _shared_model = None

    def __init__(self) -> None:
        pass

    async def embed_document(self, text: str) -> list[float]:
        return await self._encode(self._document_text(text))

    async def embed_query(self, text: str) -> list[float]:
        return await self._encode(self._query_text(text))

    async def _encode(self, text: str) -> list[float]:
        model = await self._get_model()
        return await asyncio.to_thread(self._encode_sync, model, text)

    async def _get_model(self):
        if LocalEmbeddingService._shared_model is None:
            LocalEmbeddingService._shared_model = await asyncio.to_thread(
                self._load_model,
            )
        return LocalEmbeddingService._shared_model

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer  # noqa: PLC0415
        except ImportError as exc:
            msg = 'sentence-transformers is not installed. Run `uv sync`.'
            raise RuntimeError(msg) from exc

        model = SentenceTransformer(
            settings.embeddings.model_name,
            trust_remote_code=settings.embeddings.trust_remote_code,
        )
        if settings.embeddings.max_seq_length > 0:
            model.max_seq_length = settings.embeddings.max_seq_length
        return model

    def _encode_sync(self, model, text: str) -> list[float]:
        kwargs = {'normalize_embeddings': True}

        embedding = model.encode(text, **kwargs)
        return [float(item) for item in embedding]

    def _document_text(self, text: str) -> str:
        return f'{settings.embeddings.document_prefix}{text}'

    def _query_text(self, text: str) -> str:
        if settings.embeddings.query_prefix:
            return f'{settings.embeddings.query_prefix}{text}'
        if settings.embeddings.query_instruction:
            return f'Instruct: {settings.embeddings.query_instruction}\nQuery: {text}'
        return text
