from typing import Annotated

from fastapi import Depends

from src.app.core import settings
from src.app.services.gigachat_client import GigaChatClient
from src.utils.logger import logger

SYSTEM_PROMPT = """
Ты помощник для адаптации студентов Казанского федерального университета.
Отвечай на русском языке ясно и доброжелательно.
Если вопрос требует точного адреса, контакта, срока или правила, но в запросе
нет проверенного контекста, предупреди, что информацию нужно сверить с
официальными источниками КФУ. Не придумывай точные данные.
""".strip()


class LLMService:
    def __init__(
        self,
        gigachat_client: Annotated[GigaChatClient, Depends(GigaChatClient)],
    ) -> None:
        self.gigachat_client = gigachat_client

    async def generate_answer(
        self,
        prompt: str,
        system_prompt: str = SYSTEM_PROMPT,
    ) -> tuple[str, dict]:
        if settings.llm.provider != 'gigachat':
            return settings.llm.fallback_answer, {
                'provider': settings.llm.provider,
                'llm_available': False,
                'reason': 'Unsupported LLM provider',
            }

        try:
            answer = await self.gigachat_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
            )
        except Exception as exc:
            logger.warning('LLM generation failed: %s', exc)
            return settings.llm.fallback_answer, {
                'provider': 'gigachat',
                'llm_available': False,
                'reason': str(exc),
            }

        return answer, {
            'provider': 'gigachat',
            'model': settings.gigachat.model,
            'llm_available': True,
        }
