import time
from uuid import uuid4

import httpx

from src.app.core import settings

MILLISECONDS_TIMESTAMP_THRESHOLD = 10_000_000_000


class GigaChatClient:
    def __init__(self) -> None:
        self._access_token: str | None = None
        self._expires_at: float = 0

    async def generate(self, prompt: str, system_prompt: str) -> str:
        token = await self._get_access_token()
        payload = {
            'model': settings.gigachat.model,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': prompt},
            ],
            'temperature': settings.gigachat.temperature,
            'max_tokens': settings.gigachat.max_tokens,
        }

        async with self._client() as client:
            response = await client.post(
                '/chat/completions',
                headers={'Authorization': f'Bearer {token}'},
                json=payload,
            )
            response.raise_for_status()

        data = response.json()
        choices = data.get('choices') or []
        if not choices:
            msg = 'GigaChat response does not contain choices'
            raise RuntimeError(msg)

        message = choices[0].get('message') or {}
        content = message.get('content')
        if not isinstance(content, str) or content == '':
            msg = 'GigaChat response does not contain message content'
            raise RuntimeError(msg)
        return content

    async def _get_access_token(self) -> str:
        if self._access_token is not None and time.time() < self._expires_at - 30:
            return self._access_token

        auth_key = settings.gigachat.auth_key.get_secret_value().strip()
        if auth_key == '':
            msg = 'GigaChat auth key is not configured'
            raise RuntimeError(msg)

        authorization = (
            auth_key if auth_key.startswith('Basic ') else f'Basic {auth_key}'
        )
        async with self._client(base_url=None) as client:
            response = await client.post(
                settings.gigachat.oauth_url,
                headers={
                    'Accept': 'application/json',
                    'Authorization': authorization,
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'RqUID': str(uuid4()),
                },
                data={'scope': settings.gigachat.scope},
            )
            response.raise_for_status()

        data = response.json()
        access_token = data.get('access_token')
        if not isinstance(access_token, str) or access_token == '':
            msg = 'GigaChat OAuth response does not contain access_token'
            raise RuntimeError(msg)

        self._access_token = access_token
        self._expires_at = self._parse_expires_at(data.get('expires_at'))
        return access_token

    def _client(
        self,
        base_url: str | None = settings.gigachat.base_url,
    ) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=base_url or '',
            timeout=settings.gigachat.timeout_seconds,
            verify=settings.gigachat.verify_ssl,
        )

    def _parse_expires_at(self, raw_expires_at: int | float | str | None) -> float:
        if raw_expires_at is None:
            return time.time() + 30 * 60

        expires_at = float(raw_expires_at)
        if expires_at > MILLISECONDS_TIMESTAMP_THRESHOLD:
            return expires_at / 1000
        return expires_at
