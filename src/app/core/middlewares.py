import time

from starlette.requests import Request

from src.utils.logger import logger


async def request_logging_middleware(request: Request, call_next):
    start = time.perf_counter()
    client_host = request.client.host if request.client else None

    logger.info(
        'Request started: %s %s',
        request.method,
        request.url.path,
        extra={'client_host': client_host},
    )

    try:
        response = await call_next(request)
    except Exception:
        duration_ms = (time.perf_counter() - start) * 1000
        logger.error(
            'Request failed: %s %s (%.2f ms)',
            request.method,
            request.url.path,
            duration_ms,
            extra={
                'path': request.url.path,
                'method': request.method,
                'client_host': client_host,
            },
            exc_info=True,
        )
        raise

    duration_ms = (time.perf_counter() - start) * 1000
    logger.info(
        'Request finished: %s %s -> %s (%.2f ms)',
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        extra={'client_host': client_host},
    )
    return response
