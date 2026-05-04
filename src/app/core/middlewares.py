from starlette.requests import Request

from src.utils.logger import logger


async def request_logging_middleware(request: Request, call_next):
    try:
        return await call_next(request)

    except Exception as exc:
        logger.error(
            'Unhandled exception encountered',
            extra={
                'path': request.url.path,
                'method': request.method,
                'client_host': request.client.host if request.client else None,
            },
            exc_info=True,
        )
        raise exc
