import json
from typing import Annotated, Any

from fastapi import Depends

from src.app.core import settings
from src.app.schemas.llm import ScopeClassificationResult
from src.app.services.gigachat_client import GigaChatClient
from src.utils.logger import logger

SYSTEM_PROMPT = """
Ты помощник для адаптации студентов Казанского федерального университета.
Отвечай на русском языке ясно и доброжелательно.
Если вопрос требует точного адреса, контакта, срока или правила, но в запросе
нет проверенного контекста, предупреди, что информацию нужно сверить с
официальными источниками КФУ. Не придумывай точные данные.
""".strip()

SCOPE_CLASSIFIER_SYSTEM_PROMPT = """
Ты роутер тематики для чатбота адаптации студентов КФУ.
Определи, к какой теме ближе всего относится вопрос студента.

Доступные intent:
- teacher_contact: контакты, должность, кабинет, страница преподавателя или сотрудника.
- institute_contact: контакты института, директората, деканата, адреса подразделений.
- admission: поступление, приемная комиссия, сроки приема, документы,
  магистратура, бакалавриат, образовательные программы и направления,
  бюджетные места, платное обучение, стоимость, договор.
- schedule: расписание занятий, экзаменов, сессии, календарные учебные графики.
- academic_rules: академический отпуск, переводы, отчисление, справки, правила обучения.
- student_services: общежития, стипендии, адаптация, цифровые сервисы, кампус.
- university_info: общая официальная информация о КФУ, ИТИС, программах и лабораториях.
- out_of_scope: вопрос не связан с КФУ, учебой или студенческими сервисами.

Выбери source_group:
- kpfu: контакты преподавателей, институтов, деканатов, общая информация КФУ/ИТИС.
- admissions: поступление, приемная комиссия, сроки приема, документы,
  образовательные программы, направления, бюджет, платное обучение,
  стоимость и договор.
- schedule: расписание и учебные графики.
- none: out_of_scope.

Если вопрос про сторонние бренды, развлечения, еду, фильмы, игры, погоду,
политику или другую тему без связи с КФУ и учебой, поставь out_of_scope и none.

Если вопрос про платные или бюджетные образовательные направления, стоимость
обучения, договорное обучение, программы бакалавриата/магистратуры или места
для поступления, выбери intent admission и source_group admissions.

Ответь строго JSON без markdown:
{"in_scope": true, "intent": "teacher_contact",
"source_group": "kpfu", "reason": "краткая причина"}
""".strip()

SCOPE_INTENTS = {
    'teacher_contact',
    'institute_contact',
    'admission',
    'schedule',
    'academic_rules',
    'student_services',
    'university_info',
    'out_of_scope',
}
SOURCE_GROUPS = {'kpfu', 'admissions', 'schedule', 'none'}
INTENT_SOURCE_GROUPS = {
    'admission': 'admissions',
    'schedule': 'schedule',
    'out_of_scope': 'none',
}


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

    async def classify_scope(self, question: str) -> ScopeClassificationResult:
        if settings.llm.provider != 'gigachat':
            return self._scope_result(
                scope_available=False,
                scope_allowed=False,
                scope_reason='Unsupported LLM provider',
            )

        try:
            answer = await self.gigachat_client.generate(
                prompt=f'Вопрос пользователя: {question}',
                system_prompt=SCOPE_CLASSIFIER_SYSTEM_PROMPT,
            )
        except Exception as exc:
            logger.warning('Scope classification failed: %s', exc)
            return self._scope_result(
                scope_available=False,
                scope_allowed=False,
                scope_reason=str(exc),
            )

        parsed = self._parse_json_object(answer)
        if parsed is None:
            raw_response = answer[:1000] if settings.debug else None
            return self._scope_result(
                scope_available=False,
                scope_allowed=False,
                scope_reason='Invalid scope classifier response',
                scope_raw_response=raw_response,
            )

        in_scope = self._coerce_bool(parsed.get('in_scope'))
        intent = str(parsed.get('intent') or '').strip()
        if not intent:
            intent = 'university_info' if in_scope else 'out_of_scope'
        if intent not in SCOPE_INTENTS:
            intent = 'university_info' if in_scope else 'out_of_scope'
        source_group = str(parsed.get('source_group') or '').strip()
        if source_group not in SOURCE_GROUPS:
            source_group = self._source_group_for_intent(intent, in_scope)
        reason = str(parsed.get('reason') or '').strip()
        return self._scope_result(
            scope_available=True,
            scope_allowed=in_scope,
            scope_intent=intent,
            scope_source_group=source_group,
            scope_reason=reason,
        )

    def _scope_result(self, **data: Any) -> ScopeClassificationResult:
        return ScopeClassificationResult(
            scope_provider=settings.llm.provider,
            **data,
        )

    def _source_group_for_intent(self, intent: str, in_scope: bool) -> str:
        """Map a detected topic to the trusted URL group used by web fallback."""
        if not in_scope or intent == 'out_of_scope':
            return 'none'
        return INTENT_SOURCE_GROUPS.get(intent, 'kpfu')

    def _parse_json_object(self, text: str) -> dict[str, Any] | None:
        parsed = self._load_json_object(text.strip())
        if parsed is not None:
            return parsed

        # LLM can wrap JSON with prose or code fences; keep only the object.
        start = text.find('{')
        end = text.rfind('}')
        if start == -1 or end == -1 or end < start:
            return None
        return self._load_json_object(text[start : end + 1])

    def _load_json_object(self, text: str) -> dict[str, Any] | None:
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError:
            return None
        if not isinstance(parsed, dict):
            return None
        return parsed

    def _coerce_bool(self, value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {'true', '1', 'yes', 'да'}
        return False
