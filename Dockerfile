# syntax=docker/dockerfile:1

# python:3.13-slim-bookworm — slim Debian 12 image matching app Python 3.13
FROM python:3.13-slim-bookworm AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

# Layer cache: install dependencies before application source
COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

FROM python:3.13-slim-bookworm AS runtime

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r app \
    && useradd -r -g app -d /app -s /usr/sbin/nologin app

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH" \
    LOGGING__LOG_FILE=/tmp/app.log \
    GUNICORN_WORKERS=2

COPY --from=builder --chown=app:app /app/.venv /app/.venv
COPY --chown=app:app alembic.ini gunicorn.conf.py /app/
COPY --chown=app:app migrations /app/migrations
COPY --chown=app:app scripts /app/scripts
COPY --chown=app:app src /app/src

RUN chown -R app:app /app

USER app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
    CMD curl -fsS http://127.0.0.1:8000/openapi.json

CMD ["gunicorn", "src.app.main:app", "-c", "gunicorn.conf.py"]
