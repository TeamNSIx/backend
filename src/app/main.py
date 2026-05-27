import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from src.app.core import settings
from src.app.core.handlers import register_exception_handlers
from src.app.core.middlewares import request_logging_middleware
from src.app.core.rate_limit import limiter
from src.app.routers import api_router
from src.utils.logger import setup_logger

log_level = getattr(logging, settings.logging.level.upper(), logging.INFO)
setup_logger(level=log_level, log_file=settings.logging.log_file)

app = FastAPI(title=settings.app_name, debug=settings.debug)
app.state.limiter = limiter

if settings.cors.enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins_list,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.methods_list,
        allow_headers=settings.cors.headers_list,
    )

if settings.rate_limit.enabled:
    app.add_middleware(SlowAPIMiddleware)

app.middleware('http')(request_logging_middleware)
register_exception_handlers(app)
app.include_router(api_router)
