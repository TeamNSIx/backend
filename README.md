# Чат-бот с LLM для адаптации студента КФУ

Данный проект представляет собой интеллектуального чат-бота на базе больших языковых моделей (LLM), предназначенного для помощи в адаптации студентов Казанского федерального университета. Бот помогает ориентироваться в университетской среде, отвечает на вопросы о расписании, мероприятиях, учебных процессах и структуре вуза.

## Состав команды и распределение ролей


| Имя                                                       | Роль                                |
| :----------------------------------------------------------- | :-------------------------------------- |
| **Идрисов Рамазан Омаргаджиевич** | Фронтенд-разработчик |
| **Галимов Данис Ленарович**             | Бэкенд-разработчик     |
| **Молокина Лиана Викторовна**         | Бэкенд-разработчик     |
| **Баширов Адель Тагирович**             | Фронтенд-разработчик |
| **Николаева Полина Евгеньевна**     | Фронтенд-разработчик |

## Инструкция по запуску проекта

Локальная разработка:

`uv run uvicorn src.app.main:app --reload`

Production (gunicorn + uvicorn workers, слушает `0.0.0.0`):

`uv run gunicorn src.app.main:app -c gunicorn.conf.py`

После миграций выполните bootstrap RBAC (роли, permissions, admin):

`uv run python -m scripts.bootstrap_rbac`

## Переменные окружения

Перед запуском создайте локальный файл `.env` на основе шаблона:

`cp .env.example .env`

| Название переменной | Тип | Описание | Значение по умолчанию |
|---|---|---|---|
| `APP_NAME` | `str` | Имя FastAPI приложения | `KFU Student Adaptation Chatbot` |
| `DEBUG` | `bool` | Режим отладки FastAPI/SQLAlchemy (`true`/`false`) | `false` |
| `LOGGING__LEVEL` | `str` | Уровень логирования (`DEBUG`, `INFO`, `WARNING`, …) | `INFO` |
| `LOGGING__LOG_FILE` | `str` | Путь к файлу логов приложения | `my_log.log` |
| `DB__SCHEMA` | `str` | Драйвер БД для SQLAlchemy | `postgresql+asyncpg` |
| `DB__HOST` | `str` | Хост PostgreSQL | `localhost` |
| `DB__USER` | `str` | Пользователь PostgreSQL | `YOUR_DB_USER` |
| `DB__PASSWORD` | `str` | Пароль пользователя PostgreSQL | `YOUR_DB_PASSWORD` |
| `DB__PORT` | `int` | Порт PostgreSQL | `5432` |
| `DB__NAME` | `str` | Имя базы данных PostgreSQL | `YOUR_DB_NAME` |
| `AUTH__SECRET` | `str` | Секретный ключ JWT (минимум 32 символа) | `change-this-secret-at-least-32-chars` |
| `AUTH__ALGORITHM` | `str` | Алгоритм подписи JWT | `HS256` |
| `AUTH__ACCESS_TOKEN_LIFETIME_SECONDS` | `int` | Время жизни access-токена в секундах | `3600` |
| `AUTH__REFRESH_TOKEN_LIFETIME_SECONDS` | `int` | Время жизни refresh-токена в секундах | `3600` |
| `SMTP__HOST` | `str` | Хост SMTP-сервера | `smtp.example.com` |
| `SMTP__PORT` | `int` | Порт SMTP | `587` |
| `SMTP__USERNAME` | `str` | Логин SMTP | пусто |
| `SMTP__PASSWORD` | `str` | Пароль SMTP | пусто |
| `SMTP__FROM_EMAIL` | `str` | Email отправителя | `noreply@example.com` |
| `SMTP__FROM_NAME` | `str` | Имя отправителя в письме | `KFU Chatbot` |
| `SMTP__STARTTLS` | `bool` | Использовать STARTTLS | `true` |
| `SMTP__SSL_TLS` | `bool` | Использовать SSL/TLS | `false` |
| `SMTP__USE_CREDENTIALS` | `bool` | Аутентификация на SMTP | `true` |
| `EMAIL__ENABLED` | `bool` | Включить отправку email | `true` |
| `EMAIL__FRONTEND_BASE_URL` | `str` | Базовый URL фронтенда (ссылки в письмах) | `http://localhost:3000` |
| `EMAIL__CONFIRMATION_PATH` | `str` | Путь страницы подтверждения аккаунта | `/confirm` |
| `EMAIL__CONFIRMATION_TOKEN_LIFETIME_SECONDS` | `int` | Время жизни токена подтверждения (сек) | `86400` (1 день) |
| `CORS__ENABLED` | `bool` | Включить CORS middleware | `true` |
| `CORS__ALLOW_ORIGINS` | `str` | Разрешённые origins через запятую | `http://localhost:3000,http://127.0.0.1:3000` |
| `CORS__ALLOW_CREDENTIALS` | `bool` | Разрешить cookies в CORS | `true` |
| `CORS__ALLOW_METHODS` | `str` | Разрешённые HTTP-методы через запятую | `GET,POST,PATCH,OPTIONS` |
| `CORS__ALLOW_HEADERS` | `str` | Разрешённые заголовки через запятую | `Authorization,Content-Type,Accept` |
| `RATE_LIMIT__ENABLED` | `bool` | Включить rate limiting (slowapi) | `true` |
| `RATE_LIMIT__DEFAULT` | `str` | Лимит по умолчанию для API | `60/minute` |
| `RATE_LIMIT__AUTH` | `str` | Лимит для auth-роутов | `10/minute` |
| `GUNICORN_BIND` | `str` | Адрес и порт gunicorn | `0.0.0.0:8000` |
| `GUNICORN_WORKERS` | `int` | Число worker-процессов | `4` |
| `GUNICORN_TIMEOUT` | `int` | Таймаут worker в секундах | `120` |
| `GUNICORN_KEEPALIVE` | `int` | Keep-alive в секундах | `5` |
| `GUNICORN_ACCESS_LOG` | `str` | Путь access-лога (`-` — stdout) | `-` |
| `GUNICORN_ERROR_LOG` | `str` | Путь error-лога (`-` — stderr) | `-` |
| `GUNICORN_LOG_LEVEL` | `str` | Уровень логов gunicorn | `info` |
| `RBAC__ADMIN_EMAIL` | `str` | Email учётной записи администратора (bootstrap) | `admin@example.com` |
| `RBAC__ADMIN_PASSWORD` | `str` | Пароль администратора при первом создании или если у записи ещё нет пароля | `admin-change-me` |
| `RBAC__ADMIN_ROLE_NAME` | `str` | Имя роли с полным доступом (`*` scopes) | `admin` |
| `RBAC__PUBLIC_ROLE_NAME` | `str` | Роль по умолчанию для всех пользователей после регистрации | `public` |
| `LLM__PROVIDER` | `str` | Провайдер LLM для генерации ответов | `gigachat` |
| `LLM__FALLBACK_ANSWER` | `str` | Ответ, который сохраняется при недоступности LLM | `Сообщение сохранено. LLM пока недоступна или не настроена.` |
| `GIGACHAT__AUTH_KEY` | `str` | Ключ авторизации GigaChat API. Можно указывать с префиксом `Basic ` или без него | пусто |
| `GIGACHAT__SCOPE` | `str` | Scope для OAuth-запроса GigaChat | `GIGACHAT_API_PERS` |
| `GIGACHAT__MODEL` | `str` | Модель GigaChat для генерации ответа | `GigaChat-2` |
| `GIGACHAT__BASE_URL` | `str` | Базовый URL GigaChat API | `https://gigachat.devices.sberbank.ru/api/v1` |
| `GIGACHAT__OAUTH_URL` | `str` | URL для получения access token GigaChat | `https://ngw.devices.sberbank.ru:9443/api/v2/oauth` |
| `GIGACHAT__TIMEOUT_SECONDS` | `float` | Таймаут HTTP-запросов к GigaChat в секундах | `30` |
| `GIGACHAT__VERIFY_SSL` | `bool` | Проверять SSL-сертификат GigaChat (`true`/`false`) | `true` |
| `GIGACHAT__TEMPERATURE` | `float` | Температура генерации ответа | `0.2` |
| `GIGACHAT__MAX_TOKENS` | `int` | Максимальное количество токенов в ответе | `700` |

Секретный JWT-ключ можно сгенерировать командой:

`openssl rand -hex 32`

## Подключение PostgreSQL

Проект использует асинхронное подключение к БД через `postgresql+asyncpg`.

1. Убедитесь, что локальный PostgreSQL запущен.
2. Создайте БД `kfu_chatbot` (или укажите свою в `DB__NAME`).
3. Проверьте пользователя/пароль в `.env`.
4. Для работы с `embedding` убедитесь, что в PostgreSQL установлено расширение `pgvector`.
5. Примените миграции:

`uv run alembic upgrade head`

6. Выполните bootstrap RBAC:

`uv run python -m scripts.bootstrap_rbac`

7. Запустите приложение:

`uv run uvicorn src.app.main:app --reload`

## Миграции Alembic

Структура БД управляется только через Alembic. Приложение не создаёт таблицы автоматически на старте. Bootstrap ролей, permissions и учётной записи администратора выполняется отдельным скриптом `scripts/bootstrap_rbac.py`.

Создать новую миграцию по изменениям моделей:

`uv run alembic revision --autogenerate -m "migration message"`

Применить все миграции:

`uv run alembic upgrade head`

Откатить последнюю миграцию:

`uv run alembic downgrade -1`

Показать текущую ревизию в БД:

`uv run alembic current`
